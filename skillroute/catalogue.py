"""Validated, editable role and competency catalogue."""
import json
import math
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


def validate(data):
    skills = {s['id']: s for s in data['skills']}
    if len(skills) != len(data['skills']):
        raise ValueError('Duplicate skill IDs')
    visited, active = set(), set()

    def visit(s):
        if s not in skills:
            raise ValueError(f'Unknown prerequisite: {s}')
        if s in active:
            raise ValueError('Circular prerequisites')
        if s in visited:
            return
        active.add(s)
        for p in skills[s]['prerequisites']:
            visit(p)
        active.remove(s)
        visited.add(s)
    for s in skills:
        visit(s)
        if not math.isfinite(skills[s]['hours']) or skills[s]['hours'] <= 0:
            raise ValueError('Effort must be positive')
        if len(skills[s]['prerequisites']) != len(set(skills[s]['prerequisites'])):
            raise ValueError('Duplicate prerequisite')
        for resource in skills[s]['resources']:
            url=urlparse(resource['url'])
            if url.scheme != 'https' or not url.netloc:
                raise ValueError('Resource must use an absolute HTTPS URL')
        for question in skills[s]['questions']:
            if len(question['options']) < 2 or question['answer'] not in range(len(question['options'])):
                raise ValueError('Invalid assessment answer index')
    if len({r['id'] for r in data['roles']}) != len(data['roles']):
        raise ValueError('Duplicate role IDs')
    for role in data['roles']:
        if len({r['skill'] for r in role['requirements']}) != len(role['requirements']):
            raise ValueError('Duplicate role requirement')
        for r in role['requirements']:
            if r['skill'] not in skills or not 0 < r['target'] <= 5 or not 0 < r['weight'] <= 1:
                raise ValueError('Invalid requirement')
    return data


def load():
    return validate(json.loads((ROOT / 'data/catalogue.json').read_text(encoding='utf-8')))
