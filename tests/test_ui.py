from pathlib import Path
from streamlit.testing.v1 import AppTest

PAGES=['Overview','Learner Profile','Career Roles','Skill Gap Analysis','Learning Roadmap','Assessment / Practice','Adaptive Learning','Model Lab','Progress & Reports','Settings / About']


def test_navigation_and_complete_workflow(tmp_path,monkeypatch):
    monkeypatch.setenv('SKILLROUTE_DB',str(tmp_path/'ui.db'))
    app=AppTest.from_file(str(Path(__file__).parents[1]/'app.py'),default_timeout=30).run()
    for page in PAGES:
        app.sidebar.radio[0].set_value(page).run()
        assert not app.exception, page
        assert not app.error, page
        assert app.title[0].value==page
        assert not app.json, page
    app.sidebar.radio[0].set_value('Learner Profile').run()
    app.text_input[0].set_value('UI learner')
    app.button[0].click().run()
    assert app.success
    app.sidebar.radio[0].set_value('Assessment / Practice').run()
    app.button[0].click().run()
    assert app.error[0].value=='Answer every question before submitting.'
    for radio in app.radio:
        if radio.label!='Navigate':
            radio.set_value(1)
    app.button[0].click().run()
    assert app.success
    app.sidebar.radio[0].set_value('Progress & Reports').run()
    assert not app.error
    from skillroute.database import Store
    assert Store(tmp_path/'ui.db').profile()['name']=='UI learner'
    assert len(Store(tmp_path/'ui.db').attempts())==1
    app.sidebar.radio[0].set_value('Learning Roadmap').run()
    first_status=app.selectbox[0]
    skill=first_status.key.removeprefix('status_')
    first_status.set_value('completed')
    next(b for b in app.button if b.key=='save_'+skill).click().run()
    assert Store(tmp_path/'ui.db').progress()[skill]=='completed'
    app.sidebar.radio[0].set_value('Settings / About').run()
    assert app.button[0].disabled
    app.checkbox[0].check().run()
    app.button[0].click().run()
    assert Store(tmp_path/'ui.db').attempts()==[]


def test_model_lab_training_and_inference(tmp_path,monkeypatch):
    from skillroute import ml
    monkeypatch.setenv('SKILLROUTE_DB',str(tmp_path/'models-ui.db'))
    monkeypatch.setattr(ml,'ARTIFACTS',tmp_path/'artifacts')
    app=AppTest.from_file(str(Path(__file__).parents[1]/'app.py'),default_timeout=60).run()
    app.sidebar.radio[0].set_value('Model Lab').run()
    app.button[0].click().run()
    assert not app.error
    assert ml.metadata()['records']==600
    for algorithm in ml.metadata()['models']:
        app.selectbox[0].set_value(algorithm).run()
        assert not app.error
        assert not app.exception
    next(b for b in app.button if b.label=='Run model inference').click().run()
    assert not app.error
    assert not app.json
    metrics={metric.label:metric.value for metric in app.metric}
    assert 'Estimated next score' in metrics
    assert 'Inferred mastery' in metrics
