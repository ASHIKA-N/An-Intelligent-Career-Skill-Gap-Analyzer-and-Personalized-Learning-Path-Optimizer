import copy
import io
import json
import numpy as np
import pandas as pd
import pytest
from skillroute.catalogue import load,validate
from skillroute.core import gaps,roadmap,validate_profile
from skillroute.database import Store
from skillroute.reporting import export_gaps,export_attempts
from skillroute import reinforcement as rl


@pytest.fixture
def store(tmp_path):
    result=Store(tmp_path/'test.db')
    result.seed()
    return result


def test_profile_persistence_and_validation(store):
    p=store.profile()
    p['name']='Learner A'
    p['ratings']['python']=4
    store.save_profile(p)
    assert Store(store.path).profile()==p
    for bad in [-1,6,float('nan')]:
        p['ratings']['python']=bad
        with pytest.raises(ValueError):
            store.save_profile(p)
    p['ratings']['python']=1
    p['hours']=0
    with pytest.raises(ValueError):
        store.save_profile(p)


def test_formula_missing_and_nonnegative(store):
    p=store.profile()
    p['ratings']={}
    rows=gaps(p,{'python':5},load())
    for row in rows:
        assert row['gap']>=0
        assert row['priority']==pytest.approx(100*row['gap']/5*row['weight']*(1+row['prerequisite_relevance'])/2)
        if row['skill']=='python':
            assert row['gap']==0
        else:
            assert row['current']==0


def test_cycles_rejected():
    c=copy.deepcopy(load())
    c['skills'][0]['prerequisites']=['algorithms']
    with pytest.raises(ValueError,match='Circular'):
        validate(c)


def test_roadmap_dependencies_and_completed(store):
    p=store.profile()
    p['role']='ml_engineer'
    rows=gaps(p,{},load())
    plan=roadmap(rows,load(),{},p['hours'])
    positions={s['id']:i for i,s in enumerate(plan)}
    for objective in plan:
        for dep in objective['prerequisites']:
            if dep in positions:
                assert positions[dep]<positions[objective['id']]
    store.set_progress('python','completed')
    reloaded=Store(store.path)
    assert reloaded.progress()['python']=='completed'
    assert 'python' not in [r['id'] for r in roadmap(rows,load(),reloaded.progress(),p['hours'])]
    assert len(positions)==len(plan)


def test_assessment_evidence_adaptation_and_idempotency(store):
    p=store.profile()
    p['ratings']['python']=4
    store.save_profile(p)
    store.set_progress('python','completed')
    questions=load()['skills'][0]['questions']
    wrong=[(q['answer']+1)%len(q['options']) for q in questions]
    assert store.submit('python',wrong,'attempt-1')==0
    assert store.submit('python',wrong,'attempt-1') is None
    assert len(store.attempts())==1
    assert store.profile()['ratings']['python']==4
    assert store.evidence()['python']==0
    assert store.progress()['python']=='started'
    rows=gaps(store.profile(),store.evidence(),load())
    assert next(r for r in rows if r['skill']=='python')['gap']==4
    assert 'python' in [r['id'] for r in roadmap(rows,load(),store.progress(),6)]
    assert json.loads(store.attempts()[0]['before_state'])['level']==4
    with pytest.raises(ValueError):
        store.submit('python',[99,99],'invalid')
    assert len(store.attempts())==1
    assert len(store.history())>=3


def test_export_seed_reset(store):
    rows=gaps(store.profile(),{},load())
    report=pd.read_csv(io.BytesIO(export_gaps(rows)))
    assert {'skill','current','target','gap','priority'}.issubset(report.columns)
    assert 'score' in pd.read_csv(io.BytesIO(export_attempts([]))).columns
    store.seed()
    assert len(store.history())==1
    with pytest.raises(ValueError):
        store.reset()
    store.reset(True)
    assert store.profile()['demo']
    assert store.attempts()==[]


def test_corrupt_database_actionable(tmp_path):
    path=tmp_path/'corrupt.db'
    path.write_text('not a SQLite database')
    with pytest.raises(ValueError,match='Back up'):
        Store(path)


def test_q_update_terminal_and_allowed_actions():
    q=np.zeros((3,3,2,4))
    s=(0,0,1)
    ns=(1,1,0)
    q[ns]=10
    rl.update(q,s,0,2,ns,False,alpha=.5,gamma=.9)
    assert q[s+(0,)]==pytest.approx(5.5)
    rl.update(q,s,1,2,ns,True,alpha=.5,gamma=.9)
    assert q[s+(1,)]==1
    trained=rl.train(episodes=30)
    result=rl.recommend(trained,1,20,True)
    assert result['action'] in rl.ACTIONS
    assert np.array_equal(trained,rl.train(episodes=30))
    comparison=rl.compare(trained,episodes=10)
    assert all(v['episodes']==10 for v in comparison.values())
