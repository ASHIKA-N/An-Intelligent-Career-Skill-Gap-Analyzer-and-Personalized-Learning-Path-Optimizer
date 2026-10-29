"""Rebuild the public, manually curated catalogue. No network required."""
import json
import random
from pathlib import Path

# id, name, prerequisites, resource URL, two questions (correct answer first)
ITEMS = [
('python','Python',[], 'https://docs.python.org/3/tutorial/', [('What does len([2, 4, 6]) return?', ['3','6','2']), ('Which is immutable?', ['tuple','list','dict'])]),
('sql','SQL',[], 'https://www.postgresql.org/docs/current/tutorial.html', [('Which clause filters groups after aggregation?', ['HAVING','WHERE','ORDER BY']), ('Which join retains unmatched left rows?', ['LEFT JOIN','INNER JOIN','CROSS JOIN'])]),
('statistics','Statistics',[], 'https://openstax.org/details/books/introductory-statistics-2e', [('Which is less sensitive to outliers?', ['Median','Mean','Maximum']), ('A p-value is computed assuming what?', ['The null hypothesis','The alternative is true','The sample is the population'])]),
('git','Version control',[], 'https://git-scm.com/book/en/v2', [('Which command records staged changes?', ['git commit','git fetch','git status']), ('What should normally stay out of Git?', ['API secrets','Source code','Tests'])]),
('algorithms','Algorithms',['python'], 'https://docs.python.org/3/tutorial/datastructures.html', [('Binary search requires what?', ['Sorted input','A hash table','Random input']), ('A full scan of n items is usually?', ['O(n)','O(1)','O(log n)'])]),
('testing','Testing',['python'], 'https://docs.pytest.org/en/stable/getting-started.html', [('A unit test should isolate what?', ['A small behavior','The whole internet','Production users']), ('A regression test prevents what?', ['A fixed bug returning','All future bugs','Every syntax error'])]),
('apis','HTTP APIs',['python'], 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview', [('Which method normally reads a resource?', ['GET','DELETE','PATCH']), ('HTTP 404 means?', ['Resource not found','Successful creation','Unauthorized'])]),
('databases','Database design',['sql'], 'https://www.postgresql.org/docs/current/tutorial.html', [('A foreign key enforces what?', ['Referential integrity','Sorting','Encryption']), ('A transaction should be?', ['Atomic','Always read-only','Always unlogged'])]),
('pandas','Data wrangling',['python'], 'https://pandas.pydata.org/docs/getting_started/index.html', [('How should missing data be handled?', ['Use an explicit policy','Always ignore it','Always copy the target']), ('What does groupby support?', ['Grouped aggregation','Encryption','HTTP routing'])]),
('visualization','Visualization',['statistics'], 'https://plotly.com/python/', [('Which suits two numeric variables?', ['Scatter plot','Pie chart','Word cloud']), ('A labelled y-axis should include?', ['Units when relevant','Only decoration','Private identifiers'])]),
('linear_algebra','Linear algebra',[], 'https://www.khanacademy.org/math/linear-algebra', [('An m by n matrix times n by p produces?', ['m by p','n by n','p by m']), ('A dot product returns?', ['A scalar','Always a matrix','A string'])]),
('ml','Machine learning',['statistics','pandas','linear_algebra'], 'https://scikit-learn.org/stable/getting_started.html', [('When should a scaler fit?', ['On training data only','On the entire dataset','On test labels']), ('Classification predicts?', ['Discrete labels','Only clusters','Only continuous values'])]),
('evaluation','Model evaluation',['ml'], 'https://scikit-learn.org/stable/modules/model_evaluation.html', [('Why keep a held-out test set?', ['Estimate unseen performance','Tune repeatedly','Fit preprocessing']), ('Recall measures?', ['Fraction of actual positives found','Fraction of predictions correct overall','Mean absolute error'])]),
('deployment','Model deployment',['apis','evaluation'], 'https://scikit-learn.org/stable/model_persistence.html', [('Should an untrusted pickle be loaded?', ['No, it can execute code','Yes, always','Only if renamed']), ('What should inference schema match?', ['Training feature schema','User nickname','File creation date'])]),
('communication','Technical communication',[], 'https://developers.google.com/tech-writing/overview', [('A technical report should disclose?', ['Limitations and evidence','Only successes','Invented accuracy']), ('A useful recommendation includes?', ['Reason and next action','Only a score','A hiring guarantee'])]),
('feature_engineering','Feature engineering',['pandas','statistics'], 'https://scikit-learn.org/stable/modules/preprocessing.html', [('A valid predictive feature must be?', ['Available at prediction time','Measured after the target','A personal identifier']), ('Imputation should fit on?', ['Training data','All test data','The outcome column'])]),
]


def build():
    skills=[]
    rng=random.Random(42)
    for sid, name, deps, url, qs in ITEMS:
        questions=[]
        for q, opts in qs:
            correct=opts[0]
            choices=opts.copy()
            rng.shuffle(choices)
            questions.append(dict(prompt=q,options=choices,answer=choices.index(correct),feedback=f'The correct choice is: {correct}.'))
        skills.append(dict(id=sid,name=name,prerequisites=deps,hours=6 if deps else 4,
            outcome=f'Apply {name.lower()} independently to a small reproducible task.',
            practice=f'Build a small worked example demonstrating {name.lower()}; include inputs, results and limitations.',
            completion='Submit a reproducible worked example and explain two edge cases; use the quiz as an additional check.',
            resources=[dict(title=f'{name} learning reference',provider=url.split('/')[2],url=url,status='Search suggestion: page content could not be verified' if sid in ['statistics','linear_algebra'] else 'Public reference inspected 2026-10-28; availability may change')],
            questions=questions))
    configs=[('sde','Software Development Engineer',['python','git','algorithms','testing','apis','databases','communication']),
             ('data_analyst','Data Analyst',['python','sql','statistics','pandas','visualization','communication']),
             ('data_scientist','Data Scientist',['python','sql','statistics','pandas','visualization','ml','evaluation','feature_engineering']),
             ('ml_engineer','Machine Learning Engineer',['python','git','testing','ml','evaluation','deployment','feature_engineering'])]
    roles=[dict(id=i,name=n,description=f'A curated educational competency profile for {n.lower()} preparation; not a live labour-market survey.',project='Deliver a reproducible role-focused project with tests, results, and limitations.',requirements=[dict(skill=s,target=4 if s in ['python','sql','ml'] else 3,weight=1 if j<3 else .8) for j,s in enumerate(ss)]) for i,n,ss in configs]
    Path(__file__).with_name('catalogue.json').write_text(json.dumps(dict(skills=skills,roles=roles),indent=2),encoding='utf-8')

if __name__ == '__main__':
    build()
