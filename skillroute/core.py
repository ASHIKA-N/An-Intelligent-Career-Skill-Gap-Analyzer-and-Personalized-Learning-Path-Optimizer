"""Deterministic evidence, gap, and prerequisite scheduling engine."""
import math


def validate_profile(profile, catalogue):
    if profile['role'] not in [r['id'] for r in catalogue['roles']]:
        raise ValueError('Choose a known role')
    if not 1 <= float(profile['hours']) <= 80:
        raise ValueError('Weekly study hours must be 1–80')
    if len(profile.get('name', '')) > 80 or len(profile.get('notes', '')) > 4000:
        raise ValueError('Name or project notes too long')
    if profile.get('experience') not in ['New learner', 'Some projects', 'Professional experience']:
        raise ValueError('Invalid experience level')
    ids = {s['id'] for s in catalogue['skills']}
    for s, v in profile['ratings'].items():
        if s not in ids or not math.isfinite(float(v)) or not 0 <= float(v) <= 5:
            raise ValueError('Skill ratings must be finite values from 0 to 5')


def gaps(profile, evidence, catalogue):
    skills = {s['id']: s for s in catalogue['skills']}
    role = next(r for r in catalogue['roles'] if r['id'] == profile['role'])
    requirements = {r['skill']: r.copy() for r in role['requirements']}
    def include(s):
        for p in skills[s]['prerequisites']:
            requirements.setdefault(p, {'skill': p, 'target': 2, 'weight': .5})
            include(p)
    for s in list(requirements):
        include(s)
    rows = []
    for s, req in requirements.items():
        current = evidence.get(s, profile['ratings'].get(s, 0))
        gap = max(0, req['target'] - current)
        dependents = sum(s in skills[t]['prerequisites'] for t in requirements)
        relevance = min(1, dependents / max(1, len(requirements) - 1))
        rows.append(dict(skill=s, name=skills[s]['name'], current=current, target=req['target'],
                         gap=gap, weight=req['weight'], prerequisite_relevance=relevance,
                         priority=100 * gap / 5 * req['weight'] * (1 + relevance) / 2,
                         evidence='Assessment (latest)' if s in evidence else 'Self-report / missing = 0'))
    return sorted(rows, key=lambda r: (-r['priority'], r['skill']))


def roadmap(rows, catalogue, progress, hours):
    skills = {s['id']: s for s in catalogue['skills']}
    levels = {r['skill']: r['current'] for r in rows}
    pending = {r['skill']: r for r in rows if r['gap'] > 0 and progress.get(r['skill']) != 'completed'}
    result, elapsed = [], 0
    while pending:
        eligible = [s for s in pending if not any(p in pending for p in skills[s]['prerequisites'])]
        if not eligible:
            raise ValueError('Circular prerequisites prevent scheduling')
        s = max(eligible, key=lambda s: (pending[s]['priority'], s))
        elapsed += skills[s]['hours']
        result.append({**skills[s], **pending.pop(s), 'week': math.ceil(elapsed / hours),
                       'status': progress.get(s, 'not started'),
                       'dependency_note': ', '.join(p for p in skills[s]['prerequisites'] if levels.get(p, 0) < 2)})
    return result
