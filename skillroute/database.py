"""Parameterized SQLite repository for a single local learner."""
import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from .catalogue import ROOT, load
from .core import validate_profile, gaps


def now():
    return datetime.now(timezone.utc).isoformat()


class Store:
    def __init__(self, path=None):
        self.path = str(path or ROOT / 'skillroute.db')
        try:
            with self.connect() as db:
                db.executescript('''
                CREATE TABLE IF NOT EXISTS learner_profiles(id INTEGER PRIMARY KEY, payload TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS learner_skills(profile_id INTEGER REFERENCES learner_profiles(id), skill TEXT, rating REAL CHECK(rating BETWEEN 0 AND 5), PRIMARY KEY(profile_id,skill));
                CREATE TABLE IF NOT EXISTS skill_evidence(id TEXT PRIMARY KEY, profile_id INTEGER REFERENCES learner_profiles(id), skill TEXT, level REAL, created TEXT, kind TEXT);
                CREATE TABLE IF NOT EXISTS roles(id TEXT PRIMARY KEY, payload TEXT);
                CREATE TABLE IF NOT EXISTS role_requirements(role_id TEXT REFERENCES roles(id), skill TEXT, target REAL, weight REAL, PRIMARY KEY(role_id,skill));
                CREATE TABLE IF NOT EXISTS learning_objectives(skill TEXT PRIMARY KEY, payload TEXT);
                CREATE TABLE IF NOT EXISTS learner_objective_progress(profile_id INTEGER REFERENCES learner_profiles(id), skill TEXT REFERENCES learning_objectives(skill), status TEXT, updated TEXT, PRIMARY KEY(profile_id,skill));
                CREATE TABLE IF NOT EXISTS assessment_attempts(id TEXT PRIMARY KEY, profile_id INTEGER REFERENCES learner_profiles(id), skill TEXT, score REAL, version TEXT, created TEXT, before_state TEXT, after_state TEXT);
                CREATE TABLE IF NOT EXISTS gap_history(id INTEGER PRIMARY KEY, created TEXT, role TEXT, payload TEXT);
                CREATE TABLE IF NOT EXISTS model_metadata(id TEXT PRIMARY KEY, created TEXT, payload TEXT);
                ''')
                c = load()
                for r in c['roles']:
                    db.execute('INSERT OR REPLACE INTO roles VALUES (?,?)', (r['id'], json.dumps(r)))
                    for req in r['requirements']:
                        db.execute('INSERT OR REPLACE INTO role_requirements VALUES (?,?,?,?)', (r['id'], req['skill'], req['target'], req['weight']))
                for s in c['skills']:
                    db.execute('INSERT OR REPLACE INTO learning_objectives VALUES (?,?)', (s['id'], json.dumps(s)))
        except sqlite3.DatabaseError as e:
            raise ValueError('Cannot open SQLite database. Back up skillroute.db and choose a writable, valid database path.') from e

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        try:
            with db:
                yield db
        finally:
            db.close()

    def profile(self):
        with self.connect() as db:
            row = db.execute('SELECT payload FROM learner_profiles WHERE id=1').fetchone()
        return json.loads(row[0]) if row else None

    def save_profile(self, p):
        validate_profile(p, load())
        with self.connect() as db:
            db.execute('INSERT INTO learner_profiles VALUES (1,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload', (json.dumps(p),))
            for s, rating in p['ratings'].items():
                db.execute('INSERT OR REPLACE INTO learner_skills VALUES (1,?,?)', (s, rating))
        self.snapshot()

    def seed(self):
        if self.profile() is None:
            self.save_profile(dict(name='Demo learner', role='data_analyst', hours=6, experience='New learner', preference='Documentation', notes='Synthetic demo profile. Replace with your own ratings.', demo=True, ratings={s['id']: 1 for s in load()['skills']}))

    def evidence(self):
        with self.connect() as db:
            rows = db.execute('SELECT skill,level FROM skill_evidence ORDER BY created,id').fetchall()
        return {r['skill']: r['level'] for r in rows}

    def progress(self):
        with self.connect() as db:
            return {r['skill']: r['status'] for r in db.execute('SELECT * FROM learner_objective_progress')}

    def set_progress(self, skill, status):
        if status not in ['not started', 'started', 'completed'] or skill not in {s['id'] for s in load()['skills']}:
            raise ValueError('Invalid objective or status')
        with self.connect() as db:
            db.execute('INSERT OR REPLACE INTO learner_objective_progress VALUES (1,?,?,?)', (skill, status, now()))
        self.snapshot()

    def attempts(self):
        with self.connect() as db:
            return [dict(r) for r in db.execute('SELECT * FROM assessment_attempts ORDER BY created DESC')]

    def submit(self, skill, answers, token):
        c = load()
        questions = next(s for s in c['skills'] if s['id'] == skill)['questions']
        if len(answers) != len(questions) or any(type(a) is not int or a not in range(len(q['options'])) for a, q in zip(answers, questions)):
            raise ValueError('Answer every question using a valid choice')
        p = self.profile()
        if not p:
            raise ValueError('Create a profile first')
        before = self.evidence().get(skill, p['ratings'].get(skill, 0))
        score = 100 * sum(a == q['answer'] for a, q in zip(answers, questions)) / len(questions)
        after = score / 20
        with self.connect() as db:
            if db.execute('SELECT 1 FROM assessment_attempts WHERE id=?', (token,)).fetchone():
                return None
            db.execute('INSERT INTO assessment_attempts VALUES (?,1,?,?,?,?,?,?)', (token, skill, score, '1.0', now(), json.dumps({'level': before}), json.dumps({'level': after})))
            db.execute('INSERT INTO skill_evidence VALUES (?,1,?,?,?,?)', (token, skill, after, now(), 'assessment'))
            if after < 2:
                db.execute("UPDATE learner_objective_progress SET status='started',updated=? WHERE skill=?", (now(), skill))
        self.snapshot()
        return score

    def snapshot(self):
        p = self.profile()
        if p:
            with self.connect() as db:
                db.execute('INSERT INTO gap_history(created,role,payload) VALUES (?,?,?)', (now(), p['role'], json.dumps(gaps(p, self.evidence(), load()))))

    def history(self):
        with self.connect() as db:
            return [dict(r) for r in db.execute('SELECT * FROM gap_history ORDER BY id')]

    def reset(self, confirmed=False):
        if not confirmed:
            raise ValueError('Reset requires confirmation')
        with self.connect() as db:
            for table in ['learner_objective_progress', 'assessment_attempts', 'skill_evidence', 'learner_skills', 'learner_profiles', 'gap_history']:
                db.execute(f'DELETE FROM {table}')
        self.seed()
