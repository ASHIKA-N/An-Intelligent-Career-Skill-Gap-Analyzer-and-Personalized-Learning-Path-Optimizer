import json
import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error,accuracy_score
from skillroute.features import FEATURES,features,validate_dataset
from skillroute.ml import generate,train_models


def test_actual_fit_predict_and_heldout_metrics(tmp_path):
    frame=generate(160)
    meta=train_models(frame,output=tmp_path)
    train,test=train_test_split(np.arange(len(frame)),test_size=.25,random_state=42,stratify=frame.mastery)
    ridge=joblib.load(tmp_path/'ridge.joblib')
    prediction=ridge.predict(features(frame.iloc[test]))
    assert len(prediction)==40
    assert meta['models']['Ridge']['mae']==pytest.approx(mean_absolute_error(frame.iloc[test].next_score,prediction))
    logistic=joblib.load(tmp_path/'logistic.joblib')
    assert meta['models']['Logistic Regression']['accuracy']==pytest.approx(accuracy_score(frame.iloc[test].mastery,logistic.predict(features(frame.iloc[test]))))
    assert np.allclose(ridge[0].mean_,features(frame.iloc[train]).mean())
    assert json.loads((tmp_path/'metadata.json').read_text())['test_size']==40
    assert len(json.loads((tmp_path/'q_table.json').read_text()))==3


@pytest.mark.parametrize('defect',['small','missing','duplicate','label','range','target','bands'])
def test_invalid_csv(defect):
    df=generate(160)
    if defect=='small': df=df.head(20)
    elif defect=='missing': df.loc[0,'python']=np.nan
    elif defect=='duplicate': df.loc[1,'learner_id']=df.loc[0,'learner_id']
    elif defect=='label': df.loc[0,'mastery']='hired'
    elif defect=='range': df.loc[0,'python']=8
    elif defect=='target': df.loc[0,'next_score']=101
    else: df.loc[0,'mastery']='independent' if df.loc[0,'mastery']!='independent' else 'guided'
    with pytest.raises(ValueError):
        validate_dataset(df)


def test_missing_feature_schema():
    with pytest.raises(ValueError,match='Missing feature'):
        features(pd.DataFrame({'python':[3]}))
