"""Banking Fraud & Transaction Intelligence — reproducible portfolio pipeline.
Usage: python src/analysis.py [--input data/PaySim.csv] [--demo] [--limit 500000]
Demo data is explicitly synthetic and not representative of real fraud rates.
"""
from __future__ import annotations
import argparse
import json
import sqlite3
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA, OUT, TAB = (ROOT / 'data', ROOT / 'outputs', ROOT / 'tableau')
REQUIRED = ['step','type','amount','nameOrig','oldbalanceOrg','newbalanceOrig',
            'nameDest','oldbalanceDest','newbalanceDest','isFraud','isFlaggedFraud']


def generate_demo(n=30000, seed=42):
    """Illustrative synthetic sample; not PaySim and not a bank's transactions."""
    rng = np.random.default_rng(seed)
    tx_type = rng.choice(['PAYMENT','TRANSFER','CASH_OUT','CASH_IN','DEBIT'], n,
                         p=[.36,.23,.20,.17,.04])
    amount = np.round(rng.lognormal(8.4, 1.15, n), 2)
    senders = rng.choice([f'C{i:06d}' for i in range(1, 3801)], n)
    receivers = rng.choice([f'C{i:06d}' for i in range(3801, 7001)], n)
    receivers[tx_type == 'PAYMENT'] = rng.choice([f'M{i:05d}' for i in range(1, 601)],
                                                  (tx_type == 'PAYMENT').sum())
    old_orig = np.round(amount * rng.uniform(1.2, 7, n), 2)
    old_dest = np.round(amount * rng.uniform(.2, 3, n), 2)
    new_orig = np.maximum(0, old_orig - amount)
    new_dest = old_dest + amount
    merchant = pd.Series(receivers).str.startswith('M').to_numpy()
    old_dest[merchant], new_dest[merchant] = 0, 0
    fraud = ((np.isin(tx_type, ['TRANSFER','CASH_OUT'])) &
             (amount > np.quantile(amount, .94)) &
             (rng.random(n) < .12)).astype(int)
    # Fraud labels in this DEMO are injected by the generator; do not interpret as validated truth.
    return pd.DataFrame({'step':rng.integers(1, 745, n), 'type':tx_type,
        'amount':amount,'nameOrig':senders,'oldbalanceOrg':old_orig,
        'newbalanceOrig':new_orig,'nameDest':receivers,'oldbalanceDest':old_dest,
        'newbalanceDest':new_dest,'isFraud':fraud,
        'isFlaggedFraud':((tx_type=='TRANSFER') & (amount>200000)).astype(int)})


def load_data(path, demo, limit):
    if demo:
        print('MODE: GENERATED DEMO DATA — illustrative only')
        return generate_demo(), 'DEMO (locally generated synthetic records)'
    if not path:
        raise SystemExit('Supply --input path/to/PaySim.csv OR run --demo')
    path = Path(path)
    if not path.exists():
        raise SystemExit(f'Input not found: {path}')
    frame = pd.read_csv(path, nrows=limit, low_memory=False)
    return frame, f'PaySim dataset: {path.name}' + (f' (first {limit:,} rows)' if limit else ' (full dataset)')


def validate_and_clean(df):
    missing = sorted(set(REQUIRED) - set(df.columns))
    if missing:
        raise ValueError(f'Missing columns: {missing}')
    df = df[REQUIRED].copy()
    original = len(df)
    df = df.drop_duplicates()
    for c in ['step','amount','oldbalanceOrg','newbalanceOrig','oldbalanceDest','newbalanceDest','isFraud','isFlaggedFraud']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df.dropna(subset=['step','type','amount','nameOrig','nameDest','isFraud'])
    df = df.loc[(df.amount >= 0) & (df.step >= 1) & df.isFraud.isin([0,1])].copy()
    df['isFraud'] = df.isFraud.astype('int8')
    df['isFlaggedFraud'] = df.isFlaggedFraud.fillna(0).astype('int8')
    df['step'] = df.step.astype('int32')
    df['transaction_id'] = np.arange(1, len(df)+1)
    df['day'] = ((df.step-1)//24 + 1).astype(int)
    df['hour'] = ((df.step-1)%24).astype(int)
    df['is_merchant'] = df.nameDest.str.startswith('M').astype(int)
    df['amount_band'] = pd.cut(df.amount, bins=[-1,1000,10000,50000,100000,np.inf],
         labels=['<=1k','1k–10k','10k–50k','50k–100k','>100k']).astype(str)
    df['origin_balance_delta'] = df.oldbalanceOrg - df.newbalanceOrig
    df['balance_difference'] = (df.origin_balance_delta - df.amount).abs()
    # Rule flags use amount, type and PRE-transaction origin balance only.
    # No label, post-transaction balance or PaySim pre-existing flag is used to construct risk.
    df['rule_high_amount'] = (df.amount >= 100000).astype(int)
    df['rule_low_pre_balance'] = ((df.oldbalanceOrg < df.amount) &
                                 df.oldbalanceOrg.notna()).astype(int)
    df['rule_transfer'] = df.type.isin(['TRANSFER','CASH_OUT']).astype(int)
    df['risk_score'] = (2*df.rule_high_amount + df.rule_low_pre_balance + df.rule_transfer)
    df['risk_tier'] = np.select([df.risk_score>=3,df.risk_score>=1],['High','Medium'],default='Low')
    df['rule_alert'] = (df.risk_score>=3).astype(int)
    return df, {'raw_rows':original,'clean_rows':len(df),'removed_rows':original-len(df),
                'duplicate_or_invalid_removed':original-len(df)}


def create_dimensions(df):
    # Origin and destination are account IDs, NOT verified unique real-world customers.
    orig = df[['nameOrig']].rename(columns={'nameOrig':'account_id'}).drop_duplicates()
    dest = df[['nameDest']].rename(columns={'nameDest':'account_id'}).drop_duplicates()
    accounts = pd.concat([orig,dest]).drop_duplicates().sort_values('account_id').reset_index(drop=True)
    accounts['account_type'] = np.where(accounts.account_id.str.startswith('M'),'Merchant','Customer-like')
    types = pd.DataFrame({'type':sorted(df.type.unique())})
    types['type_group'] = np.where(types.type.isin(['TRANSFER','CASH_OUT']),'Movement','Other')
    return accounts, types


def sql_analysis(df, accounts, types):
    db = OUT/'banking_intelligence.sqlite'
    with sqlite3.connect(db) as con:
        df.to_sql('transactions',con,if_exists='replace',index=False,chunksize=5000)
        accounts.to_sql('accounts',con,if_exists='replace',index=False,chunksize=5000)
        types.to_sql('transaction_types',con,if_exists='replace',index=False)
        con.execute('CREATE INDEX IF NOT EXISTS idx_tx_origin ON transactions(nameOrig)')
        con.execute('CREATE INDEX IF NOT EXISTS idx_tx_type ON transactions(type)')
        con.execute('CREATE INDEX IF NOT EXISTS idx_tx_day ON transactions(day)')
        sql_dir=ROOT/'sql'
        for sql_file in sorted(sql_dir.glob('*.sql')):
            query=sql_file.read_text()
            result=pd.read_sql_query(query,con)
            result.to_csv(OUT/f'{sql_file.stem}.csv',index=False)
            print(f'SQL {sql_file.name}: {len(result):,} rows')
    return db


def summarize(df, provenance, qa):
    n=len(df)
    positives=int(df.isFraud.sum())
    alerts=int(df.rule_alert.sum())
    tp=int(((df.rule_alert==1)&(df.isFraud==1)).sum())
    fp=int(((df.rule_alert==1)&(df.isFraud==0)).sum())
    fn=int(((df.rule_alert==0)&(df.isFraud==1)).sum())
    tn=int(((df.rule_alert==0)&(df.isFraud==0)).sum())
    result={'source':provenance,'rows':n,'fraud_labeled':positives,
            'labeled_fraud_rate_pct':round(100*positives/n,4),
            'total_amount':round(float(df.amount.sum()),2),
            'median_amount':round(float(df.amount.median()),2),
            'rule_alerts':alerts,'rule_alert_rate_pct':round(100*alerts/n,4),
            'precision':round(tp/(tp+fp),4) if tp+fp else None,
            'recall':round(tp/(tp+fn),4) if tp+fn else None,
            'confusion_matrix':{'TP':tp,'FP':fp,'FN':fn,'TN':tn},'qa':qa}
    (OUT/'summary.json').write_text(json.dumps(result,indent=2))
    pd.DataFrame([{'metric':k,'value':v} for k,v in result.items()
                  if isinstance(v,(str,int,float))]).to_csv(OUT/'kpi_summary.csv',index=False)
    return result


def create_tableau_exports(df, accounts, types):
    # Tableau-ready wide fact table; dimensions available separately for relational modeling.
    cols=['transaction_id','step','day','hour','type','amount','amount_band',
          'nameOrig','nameDest','is_merchant','isFraud','isFlaggedFraud',
          'risk_score','risk_tier','rule_alert','rule_high_amount','rule_low_pre_balance',
          'rule_transfer']
    df[cols].to_csv(TAB/'transactions_dashboard.csv',index=False)
    accounts.to_csv(TAB/'accounts.csv',index=False)
    types.to_csv(TAB/'transaction_types.csv',index=False)
    daily=(df.groupby('day',as_index=False).agg(transactions=('transaction_id','size'),
         transaction_volume=('amount','sum'),labeled_fraud=('isFraud','sum'),
         rule_alerts=('rule_alert','sum')))
    daily['fraud_rate_pct']=daily.labeled_fraud/daily.transactions*100
    daily.to_csv(TAB/'daily_metrics.csv',index=False)
    type_summary=(df.groupby('type',as_index=False).agg(transactions=('transaction_id','size'),
         transaction_volume=('amount','sum'),labeled_fraud=('isFraud','sum'),
         rule_alerts=('rule_alert','sum')))
    type_summary['fraud_rate_pct']=type_summary.labeled_fraud/type_summary.transactions*100
    type_summary.to_csv(TAB/'type_metrics.csv',index=False)
    heat=(df.groupby(['day','hour'],as_index=False).agg(transactions=('transaction_id','size'),
          labeled_fraud=('isFraud','sum'),rule_alerts=('rule_alert','sum')))
    heat.to_csv(TAB/'risk_heatmap.csv',index=False)
    return daily,type_summary


def charts(df,daily,types):
    plt.style.use('default')
    fig,ax=plt.subplots(figsize=(11,5))
    ax.plot(daily.day,daily.transactions,linewidth=2)
    ax.set(title='Transactions by simulation day',xlabel='Simulation day',ylabel='Transactions')
    fig.tight_layout();fig.savefig(OUT/'transactions_by_day.png',dpi=160);plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,5))
    ax.bar(types.type,types.fraud_rate_pct)
    ax.set(title='Labeled fraud rate by transaction type',xlabel='Type',ylabel='Fraud rate (%)')
    fig.tight_layout();fig.savefig(OUT/'fraud_rate_by_type.png',dpi=160);plt.close(fig)
    tier=df.risk_tier.value_counts().reindex(['Low','Medium','High'],fill_value=0)
    fig,ax=plt.subplots(figsize=(8,5))
    ax.bar(tier.index,tier.values)
    ax.set(title='Explainable rule-based risk tiers',ylabel='Transactions')
    fig.tight_layout();fig.savefig(OUT/'risk_tiers.png',dpi=160);plt.close(fig)


def write_report(summary, df):
    by_type=df.groupby('type').agg(transactions=('transaction_id','size'),
                                   fraud=('isFraud','sum'),alerts=('rule_alert','sum'))
    by_type['fraud_rate_pct']=100*by_type.fraud/by_type.transactions
    lines=['# Banking Fraud & Transaction Intelligence — Results', '',
           f"**Dataset:** {summary['source']}",
           f"**Transactions:** {summary['rows']:,}",
           f"**Labeled fraud cases:** {summary['fraud_labeled']:,} ({summary['labeled_fraud_rate_pct']:.4f}%)",
           f"**Rule alerts:** {summary['rule_alerts']:,} ({summary['rule_alert_rate_pct']:.4f}%)",
           f"**Rule precision:** {summary['precision']} | **Recall:** {summary['recall']}", '',
           '## Breakdown by type', '',by_type.round(3).to_markdown(),'',
           '## Interpretation and limitations','',
           '- A rule alert is **not** proof of fraud. Labels are synthetic simulation outcomes.',
           '- Risk thresholds are illustrative, not validated bank policy.',
           '- PaySim step represents a simulated hour, not a real calendar timestamp.',
           '- Account IDs are not verified distinct human customers.',
           '- Balance changes may reflect simulator behavior; they are used for diagnostics, not rule flags.',
           '- When using --limit, results describe only the first N rows, not a random sample.',
           '- The project does not claim production fraud-detection performance.', '']
    (ROOT/'RESULTS.md').write_text('\n'.join(lines))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--input',type=str,help='Path to PaySim CSV')
    parser.add_argument('--demo',action='store_true',help='Generate clearly labeled illustrative data')
    parser.add_argument('--limit',type=int,default=None,help='Optional first N rows for laptop memory')
    args=parser.parse_args()
    if args.demo and args.input: parser.error('Choose --demo or --input, not both')
    for folder in [DATA,OUT,TAB]:folder.mkdir(parents=True,exist_ok=True)
    raw,source=load_data(args.input,args.demo,args.limit)
    df,qa=validate_and_clean(raw)
    if df.empty: raise ValueError('No valid rows after cleaning')
    accounts,types=create_dimensions(df)
    print('Rows:',len(df),'Accounts:',len(accounts),'Types:',len(types))
    db=sql_analysis(df,accounts,types)
    summary=summarize(df,source,qa)
    daily,by_type=create_tableau_exports(df,accounts,types)
    charts(df,daily,by_type)
    write_report(summary,df)
    print('SUCCESS — SQL database:',db)
    print('Tableau exports:',TAB)
    print('Results:',ROOT/'RESULTS.md')

if __name__=='__main__':main()
