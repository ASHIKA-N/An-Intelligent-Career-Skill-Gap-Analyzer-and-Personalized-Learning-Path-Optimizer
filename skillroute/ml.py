"""Reproducible synthetic benchmark, training, held-out evaluation and inference."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score, classification_report, confusion_matrix, accuracy_score, silhouette_score
from .catalogue import ROOT
from .features import FEATURES, LABELS, features, validate_dataset
from .reinforcement import train as train_q, compare

ARTIFACTS=ROOT/'models/artifacts'
DEMO=ROOT/'data/synthetic_assessments.csv'


def generate(n=600,seed=42):
    rng=np.random.default_rng(seed)
    latent=rng.beta(2,2,n)
    python=np.clip(5*latent+rng.normal(0,.7,n),0,5)
    stats=np.clip(5*latent+rng.normal(0,.9,n),0,5)
    hours=rng.integers(1,21,n)
    prior=np.clip(100*latent+rng.normal(0,12,n),0,100)
    projects=np.clip(rng.poisson(3*latent),0,30)
    # Unobserved motivation and observation noise deliberately limit predictability.
    outcome=np.clip(12+6*python+3*stats+.23*prior+1.2*np.sqrt(hours)+2*projects+rng.normal(0,12,n),0,100)
    df=pd.DataFrame(dict(learner_id=[f'synthetic-{i:04}' for i in range(n)],python=python,statistics=stats,practice_hours=hours,prior_score=prior,projects=projects,next_score=outcome))
    df['mastery']=pd.cut(df.next_score,[-1,45,70,100],labels=LABELS).astype(str)
    return df


def train_models(frame, source='Synthetic educational benchmark', output=None):
    frame=validate_dataset(frame)
    output=Path(output or ARTIFACTS)
    output.mkdir(parents=True,exist_ok=True)
    x=features(frame)
    train_idx,test_idx=train_test_split(np.arange(len(frame)),test_size=.25,random_state=42,stratify=frame.mastery)
    xt,xv=x.iloc[train_idx],x.iloc[test_idx]
    meta={'version':'1.0','timestamp':datetime.now(timezone.utc).isoformat(),'source':source,'records':len(frame),'features':FEATURES,
          'data_sha256':hashlib.sha256(frame.to_csv(index=False).encode()).hexdigest(),'seed':42,'split':'75/25 stratified by mastery; independent unique learners; preprocessing fit on training only; fixed hyperparameters, no test tuning',
          'train_size':len(xt),'test_size':len(xv),'class_balance':frame.mastery.value_counts().to_dict(),'test_class_balance':frame.iloc[test_idx].mastery.value_counts().to_dict(),'models':{}}
    ridge=make_pipeline(StandardScaler(),Ridge(alpha=1))
    ridge.fit(xt,frame.iloc[train_idx].next_score)
    prediction=ridge.predict(xv)
    truth=frame.iloc[test_idx].next_score
    meta['models']['Ridge']={'target':'next_score (0–100)', 'mae':mean_absolute_error(truth,prediction),'rmse':root_mean_squared_error(truth,prediction),'r2':r2_score(truth,prediction)}
    joblib.dump(ridge,output/'ridge.joblib')
    for name,estimator in [('Logistic Regression',LogisticRegression(max_iter=1000)),('Decision Tree',DecisionTreeClassifier(max_depth=5,min_samples_leaf=8,random_state=42))]:
        pipe=make_pipeline(StandardScaler(),estimator)
        pipe.fit(xt,frame.iloc[train_idx].mastery)
        prediction=pipe.predict(xv)
        truth=frame.iloc[test_idx].mastery
        meta['models'][name]={'target':'next assessment mastery band (<=45, <=70, >70)', 'accuracy':accuracy_score(truth,prediction),
            'report':classification_report(truth,prediction,labels=LABELS,output_dict=True,zero_division=0),
            'confusion_matrix':confusion_matrix(truth,prediction,labels=LABELS).tolist(),'labels':LABELS}
        joblib.dump(pipe,output/('logistic.joblib' if name.startswith('Logistic') else 'tree.joblib'))
    cluster=make_pipeline(StandardScaler(),KMeans(n_clusters=3,n_init=10,random_state=42))
    cluster.fit(xt)
    labels=cluster.predict(xv)
    transformed=cluster[0].transform(xv)
    diagnostic=float(silhouette_score(transformed,labels)) if 1<len(set(labels))<len(labels) else None
    profiles=xt.assign(cluster=cluster.predict(xt)).groupby('cluster').mean().round(3).to_dict(orient='index')
    meta['models']['K-Means']={'target':'None; scaled feature grouping', 'heldout_silhouette':diagnostic, 'diagnostic_sample_size':len(xv),'training_cluster_profiles':profiles}
    joblib.dump(cluster,output/'clusters.joblib')
    q=train_q()
    (output/'q_table.json').write_text(json.dumps(q.tolist()),encoding='utf-8')
    meta['simulation']=compare(q)
    (output/'metadata.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
    return meta


def metadata():
    path=ARTIFACTS/'metadata.json'
    required=['ridge.joblib','logistic.joblib','tree.joblib','clusters.joblib','q_table.json']
    if not path.exists() or any(not (ARTIFACTS/f).is_file() for f in required):
        return None
    return json.loads(path.read_text(encoding='utf-8'))


def predict(frame):
    # Only artifacts produced in the fixed local training directory may be loaded.
    x=features(frame)
    return {'estimated_next_score':float(joblib.load(ARTIFACTS/'ridge.joblib').predict(x)[0]),
            'inferred_mastery':str(joblib.load(ARTIFACTS/'logistic.joblib').predict(x)[0]),
            'cluster':int(joblib.load(ARTIFACTS/'clusters.joblib').predict(x)[0])}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--csv',type=Path)
    args=parser.parse_args()
    if args.csv:
        frame=pd.read_csv(args.csv)
        source='User-supplied CSV; provenance must be established by its owner'
    else:
        frame=generate()
        frame.to_csv(DEMO,index=False)
        source='Synthetic educational benchmark, seed 42 (not real students)'
    meta=train_models(frame,source)
    print(json.dumps(meta,indent=2))

if __name__=='__main__':
    main()
