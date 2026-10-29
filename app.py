"""SkillRoute — local, evidence-aware career learning companion."""
import json
import logging
import os
import uuid
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from skillroute.catalogue import load, ROOT
from skillroute.database import Store
from skillroute.core import gaps, roadmap
from skillroute import ml, reinforcement as rl
from skillroute.features import learner_features
from skillroute.reporting import export_gaps, export_attempts

st.set_page_config(page_title='SkillRoute',page_icon='S',layout='wide')
logging.basicConfig(level=logging.INFO)
PAGES=['Overview','Learner Profile','Career Roles','Skill Gap Analysis','Learning Roadmap','Assessment / Practice','Adaptive Learning','Model Lab','Progress & Reports','Settings / About']
ACTIVITY_LABELS={
    'review_prerequisite': 'Review a foundation skill',
    'practice_weak_skill': 'Practise this skill',
    'advance_skill': 'Try a harder task',
    'review_mistakes': 'Review recent mistakes',
}


@st.cache_resource
def policy():
    return rl.train()


def chart_gaps(rows):
    frame=pd.DataFrame(rows)
    chart=px.bar(frame,x='name',y=['current','target'],barmode='group',title='Current evidence and role target',labels={'value':'Proficiency (0–5)','name':'Skill','variable':'Level type'})
    chart.update_yaxes(range=[0,5])
    st.plotly_chart(chart,width='stretch')


def main():
    catalogue=load()
    store=Store(os.environ.get('SKILLROUTE_DB'))
    store.seed()
    p=store.profile()
    evidence=store.evidence()
    rows=gaps(p,evidence,catalogue)
    progress=store.progress()
    plan=roadmap(rows,catalogue,progress,p['hours'])
    attempts=store.attempts()
    skills={s['id']:s for s in catalogue['skills']}
    roles={r['id']:r for r in catalogue['roles']}
    st.sidebar.title('SkillRoute')
    st.sidebar.caption('Evidence → learning → progress')
    page=st.sidebar.radio('Navigate',PAGES)
    st.sidebar.divider()
    st.sidebar.caption('Local SQLite storage · No API key required')
    st.title(page)
    if p.get('demo'):
        st.warning('Synthetic demo profile. Edit Learner Profile to use your own ratings. Model benchmarks and adaptive simulations use synthetic data, never real placement outcomes.')
    st.caption('Educational planning tool. Readiness is not a hiring probability; quizzes are not certifications.')

    if page=='Overview':
        st.subheader(roles[p['role']]['name'])
        a,b,c=st.columns(3)
        a.metric('Objectives completed',sum(v=='completed' for v in progress.values()))
        b.metric('Objectives remaining',len(plan))
        c.metric('Study time',f"{p['hours']} hours / week")
        if plan:
            st.info(f"Next: {plan[0]['name']} — {plan[0]['outcome']}")
        else:
            st.success('No unfinished gap objectives. Use assessments to validate your estimates.')
        st.subheader('Most important gaps')
        st.dataframe(pd.DataFrame(rows[:5])[['name','gap','priority','evidence']],hide_index=True)
        st.subheader('Recent assessments')
        if attempts:
            st.dataframe(pd.DataFrame(attempts[:5])[['created','skill','score','version']],hide_index=True)
        else:
            st.info('No attempts yet. Open Assessment / Practice to add evidence.')

    elif page=='Learner Profile':
        st.write('Self-ratings are subjective. Project notes are self-reported evidence, not independently verified.')
        st.caption('0 no exposure · 1 awareness · 2 guided tasks · 3 independent common tasks · 4 complex tasks · 5 advanced consistent performance')
        with st.form('profile'):
            name=st.text_input('Nickname (optional)',p['name'],max_chars=80)
            role=st.selectbox('Target role',list(roles),index=list(roles).index(p['role']),format_func=lambda x:roles[x]['name'])
            experience=st.selectbox('Experience',['New learner','Some projects','Professional experience'],index=['New learner','Some projects','Professional experience'].index(p['experience']))
            hours=st.number_input('Weekly study hours',1,80,int(p['hours']))
            preference=st.selectbox('Preferred resource type',['Documentation','Video','Practice'],index=['Documentation','Video','Practice'].index(p.get('preference','Documentation')))
            notes=st.text_area('Project experience and evidence notes',p.get('notes',''),max_chars=4000)
            st.caption('The initial catalogue provides documentation resources. Format preference is recorded for future curation.')
            ratings={}
            cols=st.columns(2)
            for i,s in enumerate(skills.values()):
                with cols[i%2]:
                    ratings[s['id']]=st.slider(s['name'],0,5,int(p['ratings'].get(s['id'],0)))
            if st.form_submit_button('Save profile'):
                store.save_profile(dict(name=name,role=role,experience=experience,hours=hours,preference=preference,notes=notes,ratings=ratings,demo=False))
                st.success('Profile saved. Roadmap recalculates from your latest profile and evidence.')

    elif page=='Career Roles':
        role=st.selectbox('Browse role',list(roles),format_func=lambda x:roles[x]['name'])
        st.write(roles[role]['description'])
        st.dataframe(pd.DataFrame(roles[role]['requirements']),hide_index=True)
        st.write('Project:',roles[role]['project'])
        for req in roles[role]['requirements']:
            s=skills[req['skill']]
            with st.expander(s['name']):
                st.write('Prerequisites:',', '.join(s['prerequisites']) or 'None')
                st.write(s['practice'])
                for r in s['resources']:
                    st.link_button(r['title'],r['url'])
                    st.caption(r['status'])
        st.caption('Maintainers can edit data/catalogue.json; prerequisite cycles and invalid requirements are rejected on load.')

    elif page=='Skill Gap Analysis':
        st.write('Current estimate = latest assessment score ÷ 20, otherwise self-rating. Missing self-ratings explicitly default to 0. Project notes never automatically increase proficiency.')
        st.code('gap = max(0, target − current)\nrelevance = direct dependent skills / max(1, required skills − 1)\npriority = 100 × (gap / 5) × importance × (1 + relevance) / 2')
        st.caption('Priority is normalized to 0–100. Dependencies include a target-2, weight-0.5 foundation when absent from the role. Evidence type is shown; no statistical confidence is claimed.')
        chart_gaps(rows)
        selected=st.multiselect('Filter skills',list(skills),format_func=lambda x:skills[x]['name'])
        st.dataframe(pd.DataFrame([r for r in rows if not selected or r['skill'] in selected]),hide_index=True)

    elif page=='Learning Roadmap':
        st.write('Prerequisites come first; priority breaks ties. Completing a topic is your declaration. A later score below 40% reopens it for practice. Resources remain available under Career Roles.')
        if not plan:
            st.success('No unfinished gap objectives. Review completed objectives below or assess your skills.')
        for objective in plan:
            sid=objective['id']
            with st.expander(f"Week {objective['week']} · {objective['name']} · {objective['hours']} hours"):
                st.write(objective['outcome'])
                st.write('Prerequisites:',', '.join(objective['prerequisites']) or 'None')
                if objective['dependency_note']:
                    st.info('Foundation work is scheduled first: '+objective['dependency_note'])
                st.write('Practice:',objective['practice'])
                st.write('Completion criteria:',objective['completion'])
                for resource in objective['resources']:
                    st.link_button(resource['title'],resource['url'])
                    st.caption(resource['status'])
                status=st.selectbox('Objective status',['not started','started','completed'],index=['not started','started','completed'].index(objective['status']),key='status_'+sid)
                if st.button('Save progress',key='save_'+sid):
                    store.set_progress(sid,status)
                    st.rerun()
        completed=[s for s,v in progress.items() if v=='completed']
        if completed:
            st.subheader('Completed objectives')
            st.write(', '.join(skills[s]['name'] for s in completed))
            reopen=st.selectbox('Reopen objective',completed,format_func=lambda s:skills[s]['name'])
            if st.button('Reopen for practice'):
                store.set_progress(reopen,'started')
                st.rerun()

    elif page=='Assessment / Practice':
        st.write('Two-question formative checks, version 1.0. Latest score replaces the current estimate with score ÷ 20. Self-ratings and previous attempts remain unchanged. This small question bank cannot establish broad mastery.')
        sid=st.selectbox('Skill to assess',list(skills),format_func=lambda s:skills[s]['name'])
        st.session_state.setdefault('attempt_token',str(uuid.uuid4()))
        with st.form('assessment_'+sid):
            answers=[]
            for i,q in enumerate(skills[sid]['questions']):
                answers.append(st.radio(q['prompt'],list(range(len(q['options']))),format_func=lambda j,q=q:q['options'][j],index=None,key=f'q_{sid}_{i}'))
            if st.form_submit_button('Submit assessment'):
                if any(a is None for a in answers):
                    st.error('Answer every question before submitting.')
                else:
                    before=evidence.get(sid,p['ratings'].get(sid,0))
                    score=store.submit(sid,answers,st.session_state.attempt_token)
                    st.session_state.attempt_token=str(uuid.uuid4())
                    st.success(f'Saved score: {score:.0f}%. Skill estimate: {before:.1f} → {score/20:.1f}. Open Adaptive Learning or Roadmap to inspect the change.')
                    for q in skills[sid]['questions']:
                        st.write(q['feedback'])

    elif page=='Adaptive Learning':
        st.warning('Q-learning is trained in a simulated educational environment, not on real learners. Rewards encode assumed learning dynamics and do not demonstrate educational efficacy.')
        st.write('The baseline selects prerequisite review when pending, mistake review after weak performance, then practice or advancement on the highest-priority eligible gap. Q-learning chooses an activity for that same gap.')
        if attempts:
            last=attempts[0]
            st.write('Latest assessment:',last['skill'])
            before=json.loads(last['before_state'])['level']
            after=json.loads(last['after_state'])['level']
            st.write(f'Before: {before:.1f}/5 → After: {after:.1f}/5. Latest evidence replaces the skill estimate; gap priorities and the prerequisite roadmap are recomputed.')
        target=plan[0]['id'] if plan else rows[0]['skill']
        row=next(r for r in rows if r['skill']==target)
        pending=any(next((r['current'] for r in rows if r['skill']==s),0)<2 for s in skills[target]['prerequisites'])
        result=rl.recommend(policy(),row['current'],attempts[0]['score'] if attempts else 0,pending)
        st.subheader('Next activity for '+skills[target]['name'])
        with st.container(border=True):
            st.caption('RECOMMENDED ACTIVITY')
            st.subheader(ACTIVITY_LABELS[result['action']])
            st.write(skills[target]['practice'])
            current,foundation=st.columns(2)
            current.metric('Current skill estimate',f"{row['current']:.1f} / 5")
            foundation.metric('Foundation review', 'Needed' if pending else 'Not needed')
            st.caption('Baseline recommendation: '+ACTIVITY_LABELS[result['baseline']])
        st.write('Selection reason: first unfinished prerequisite-eligible objective, ordered by gap priority. The state bins its mastery, latest assessment band, and pending foundation work; the learned action maximizes that state’s Q value.')
        with st.expander('Compare learning strategies'):
            comparison=pd.DataFrame(rl.compare(policy())).T.rename(columns={'mean_reward':'Mean episode reward','std_reward':'Reward standard deviation','episodes':'Episodes'})
            comparison.index.name='Strategy'
            st.dataframe(comparison.style.format({'Mean episode reward':'{:.2f}','Reward standard deviation':'{:.2f}','Episodes':'{:.0f}'}),width='stretch')
            st.caption('Measured in the simulated environment; higher reward does not prove better real-world learning.')
        with st.expander('Environment and reproducibility'):
            st.caption('Activity values learned for the current state; these are simulated rewards, not probabilities.')
            st.dataframe(pd.DataFrame([{'Activity':ACTIVITY_LABELS[action],'Learned value':value} for action,value in result['q_values'].items()]),hide_index=True,width='stretch')
            st.write('State: mastery bins floor(level/2), capped at 2; score bins floor(score/34), capped at 2; prerequisite flag. Four actions shown above. Seed 42, 1,800 episodes, at most 12 steps; alpha=0.2, gamma=0.9, epsilon=0.15. Terminal: top mastery and performance bands, no pending prerequisite.')
            st.write('Reward: +2 success, −0.5 failure, additional −0.5 unsuitable action, −0.1 time cost. Assumed success probability: 0.8 for baseline-suitable actions, 0.25 otherwise. Evaluation: 200 unseen seeds 10000–10199, both policies start from matching states. This environment favors its encoded baseline by construction.')
            st.code('Q[s,a] += alpha * (reward + gamma * max(Q[next_state]) - Q[s,a])\n# Terminal or step-limit transition: omit future value')

    elif page=='Model Lab':
        st.warning('Synthetic educational data does not establish validity for real learning outcomes or hiring. Model inferences are separate from assessment evidence and never update your skills.')
        st.write('Train real scikit-learn pipelines on a synthetic benchmark, or validate a replacement CSV. No model uploads or untrusted pickle files are accepted.')
        upload=st.file_uploader('Replacement CSV (maximum 2 MB)',type=['csv'])
        st.caption('Required columns: learner_id, python, statistics, practice_hours, prior_score, projects, next_score, mastery. One record per learner. See data/README.md.')
        if st.button('Train and evaluate models'):
            if upload is not None and upload.size>2*1024*1024:
                st.error('CSV exceeds the 2 MB limit.')
            else:
                try:
                    with st.spinner('Fitting pipelines and evaluating held-out records…'):
                        frame=pd.read_csv(upload) if upload is not None else ml.generate()
                        meta=ml.train_models(frame,'User-supplied CSV; provenance unverified' if upload else 'Synthetic educational benchmark, seed 42 (not real students)')
                        with store.connect() as db:
                            db.execute('INSERT INTO model_metadata VALUES (?,?,?)',(str(uuid.uuid4()),meta['timestamp'],json.dumps(meta)))
                    st.success('Training and held-out evaluation completed; artifacts saved locally.')
                except (ValueError,TypeError,pd.errors.ParserError,UnicodeError) as error:
                    st.error(str(error))
        meta=ml.metadata()
        if meta is None:
            st.info('No trained artifacts yet. Use the training button or python -m skillroute.ml.')
        else:
            st.write(f"Source: {meta['source']} · {meta['records']} records · held-out n={meta['test_size']} · seed {meta['seed']}")
            st.write(meta['split'])
            st.write('Features:',', '.join(meta['features']))
            with st.expander('Dataset class distribution'):
                st.dataframe(pd.DataFrame([{'Mastery category':label.title(),'All records':count,'Held-out records':meta['test_class_balance'].get(label,0)} for label,count in meta['class_balance'].items()]),hide_index=True,width='stretch')
            algorithm=st.selectbox('Inspect trained algorithm',list(meta['models']))
            result=meta['models'][algorithm]
            st.write('Target:',result['target'])
            if algorithm=='Ridge':
                st.dataframe(pd.DataFrame([result]).drop(columns=['target']))
                st.caption('MAE/RMSE in assessment points; R² may be negative and is uncertain with small samples. Scores can extrapolate outside 0–100.')
            elif 'report' in result:
                st.metric('Held-out accuracy',f"{result['accuracy']:.3f}")
                st.dataframe(pd.DataFrame(result['report']).T)
                st.plotly_chart(px.imshow(result['confusion_matrix'],x=result['labels'],y=result['labels'],text_auto=True,labels={'x':'Predicted class','y':'True class','color':'Record count'},title='Held-out confusion matrix'),width='stretch')
            else:
                st.write('Held-out silhouette:',result['heldout_silhouette'])
                st.dataframe(pd.DataFrame(result['training_cluster_profiles']).T)
                st.caption('Cluster numbers are arbitrary feature groupings, not verified learner categories. Diagnostic uses the held-out sample after fitting on training data.')
            with st.expander('Infer from current profile (experimental)'):
                st.write('Get an experimental estimate from your current profile. This estimate does not change your recorded skills.')
                with st.expander('Inputs and limitations'):
                    st.caption('Uses Python and statistics evidence, weekly study hours and your latest quiz score. Without an assessment, the prior score is 0. Project count is 0 because project notes do not verify a count. These inputs can differ from the training benchmark.')
                if st.button('Run model inference'):
                    prediction=ml.predict(learner_features(p,evidence,attempts))
                    with st.container(border=True):
                        score,mastery=st.columns(2)
                        score.metric('Estimated next score',f"{prediction['estimated_next_score']:.1f} / 100")
                        mastery.metric('Inferred mastery',prediction['inferred_mastery'].title())
                        st.caption(f"Feature group: {prediction['cluster']} · An arbitrary cluster label, not an ability ranking. Estimates may extend beyond the assessment scale.")
            with st.expander('Training details'):
                st.dataframe(pd.DataFrame([
                    {'Detail':'Model version','Value':meta['version']},
                    {'Detail':'Trained at (UTC)','Value':meta['timestamp']},
                    {'Detail':'Training records','Value':str(meta['train_size'])},
                    {'Detail':'Held-out records','Value':str(meta['test_size'])},
                    {'Detail':'Random seed','Value':str(meta['seed'])},
                    {'Detail':'Dataset source','Value':meta['source']},
                ]),hide_index=True,width='stretch')
                st.caption('Dataset fingerprint (SHA-256)')
                st.text(meta['data_sha256'])

    elif page=='Progress & Reports':
        st.subheader('Learning progress')
        completed=sum(v=='completed' for v in progress.values())
        started=sum(v=='started' for v in progress.values())
        done_col,active_col,next_col=st.columns(3)
        done_col.metric('Completed',completed)
        active_col.metric('In progress',started)
        next_col.metric('Remaining objectives',len(plan))
        if progress:
            st.dataframe(pd.DataFrame([{'Skill':skills[s]['name'],'Status':{'started':'In progress','completed':'Completed','not started':'Not started'}[status]} for s,status in progress.items()]),hide_index=True,width='stretch')
        else:
            st.info('Your learning progress will appear here after you start or complete a roadmap objective.')
        st.subheader('Assessment history')
        if attempts:
            frame=pd.DataFrame(attempts)
            st.dataframe(frame[['created','skill','score','version']],hide_index=True)
            changes=[]
            for attempt in attempts:
                changes.append({'date':attempt['created'],'skill':attempt['skill'],'level':json.loads(attempt['after_state'])['level']})
            st.plotly_chart(px.line(pd.DataFrame(changes).sort_values('date'),x='date',y='level',color='skill',markers=True,title='Assessment-derived skill levels over time',labels={'date':'Attempt date (UTC)','level':'Proficiency (0–5)'}),width='stretch')
        else:
            st.info('Complete an assessment to see skill changes and history.')
        history=store.history()
        summaries=[dict(date=h['created'],role=h['role'],weighted_gap=sum(r['gap']*r['weight'] for r in json.loads(h['payload']))) for h in history]
        st.dataframe(pd.DataFrame(summaries),hide_index=True)
        st.caption('Historical weighted gap is sum(gap × role weight); compare within the same role. Snapshots are recorded after profile, assessment, and progress changes.')
        st.download_button('Export current gap report',export_gaps(rows),'skillroute_gaps.csv','text/csv')
        st.download_button('Export assessment history',export_attempts(attempts),'skillroute_assessments.csv','text/csv')

    elif page=='Settings / About':
        st.write('SkillRoute stores one learner locally in skillroute.db. It needs no account, hosted service, or API key. Do not expose this single-user prototype publicly or store sensitive personal information.')
        st.write('Role requirements are curated educational assumptions, not a job-market dataset. Synthetic benchmark: 600 independent learner records, fixed seed 42, noisy generated future scores. Class labels are score bands; models learn this synthetic process. No real hiring validity is established.')
        st.write('Reset deletes the local profile, skills, assessment evidence, attempts and progress, then recreates the demo profile. Curated catalogue and trained artifacts remain.')
        confirm=st.checkbox('I confirm deletion of local learner data')
        if st.button('Reset learner data',disabled=not confirm):
            store.reset(confirmed=confirm)
            st.session_state.clear()
            st.rerun()
        st.caption('Methodology: deterministic gap engine + held-out supervised benchmark + scaled clustering + simulated tabular reinforcement learning. See README.md and docs/ for reproducible methods and limitations.')


try:
    main()
except Exception:
    logging.exception('SkillRoute operation failed')
    st.error('The operation could not finish. Check the local application log. Verify that the database is writable and catalogue/model files are valid. Your data has not been intentionally reset.')
