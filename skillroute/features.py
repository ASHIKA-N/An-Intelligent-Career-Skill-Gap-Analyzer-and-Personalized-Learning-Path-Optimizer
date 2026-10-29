"""Shared, prediction-time numeric schema and strict replacement-CSV validation."""
import numpy as np
import pandas as pd

FEATURES=['python','statistics','practice_hours','prior_score','projects']
LABELS=['developing','guided','independent']


def features(frame):
    if not set(FEATURES).issubset(frame.columns):
        raise ValueError('Missing feature columns: '+', '.join(FEATURES))
    result=frame[FEATURES].apply(pd.to_numeric,errors='raise')
    bounds={'python':(0,5),'statistics':(0,5),'practice_hours':(1,80),'prior_score':(0,100),'projects':(0,30)}
    if not np.isfinite(result.to_numpy()).all():
        raise ValueError('Missing or non-finite feature values are not accepted')
    for col,(low,high) in bounds.items():
        if not result[col].between(low,high).all():
            raise ValueError(f'{col} must be between {low} and {high}')
    return result


def validate_dataset(frame):
    required={'learner_id','next_score','mastery',*FEATURES}
    if not required.issubset(frame.columns):
        raise ValueError('CSV requires: '+', '.join(sorted(required)))
    if len(frame)<100:
        raise ValueError('Not enough data: provide at least 100 independent learner records')
    features(frame)
    if frame.isna().any().any() or frame.learner_id.duplicated().any() or frame[FEATURES].duplicated().any():
        raise ValueError('Missing values, repeated learners and duplicate feature records are not accepted')
    score=pd.to_numeric(frame.next_score,errors='raise')
    if not score.between(0,100).all():
        raise ValueError('next_score must be 0–100')
    if set(frame.mastery)!=set(LABELS) or frame.mastery.value_counts().min()<10:
        raise ValueError('Require all three mastery labels with at least 10 records each')
    expected=pd.cut(score,[-1,45,70,100],labels=LABELS).astype(str)
    if not (expected==frame.mastery).all():
        raise ValueError('mastery must match next_score bands: <=45, <=70, >70')
    return frame


def learner_features(profile, evidence, attempts):
    return features(pd.DataFrame([dict(python=evidence.get('python',profile['ratings'].get('python',0)),
        statistics=evidence.get('statistics',profile['ratings'].get('statistics',0)),
        practice_hours=profile['hours'],prior_score=attempts[0]['score'] if attempts else 0,
        projects=0)]))
