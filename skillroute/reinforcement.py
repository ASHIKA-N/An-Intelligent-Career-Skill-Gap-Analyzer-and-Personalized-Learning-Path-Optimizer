"""Tabular Q-learning in an explicitly SIMULATED educational environment."""
import numpy as np

ACTIONS = ('review_prerequisite', 'practice_weak_skill', 'advance_skill', 'review_mistakes')
ALPHA, GAMMA, EPSILON = .2, .9, .15


def state(level, score, prerequisite):
    return (min(2, int(level / 2)), min(2, int(score / 34)), int(bool(prerequisite)))


def baseline(s):
    return 0 if s[2] else (3 if s[1] == 0 else (1 if s[0] < 2 else 2))


def update(q, s, a, reward, next_s, terminal, alpha=ALPHA, gamma=GAMMA):
    q[s + (a,)] += alpha * (reward + (0 if terminal else gamma * q[next_s].max()) - q[s + (a,)])


def transition(s, a, rng):
    mastery, band, prereq = s
    suitable = a == baseline(s)
    success = rng.random() < (.8 if suitable else .25)
    if success:
        if prereq and a == 0:
            prereq = 0
        else:
            mastery = min(2, mastery + 1)
        band = min(2, band + 1)
    terminal = mastery == 2 and band == 2 and not prereq
    return (mastery, band, prereq), (2 if success else -.5) - (.5 if not suitable else 0) - .1, terminal


def train(seed=42, episodes=1800):
    rng = np.random.default_rng(seed)
    q = np.zeros((3,3,2,4))
    for _ in range(episodes):
        s = (int(rng.integers(2)), int(rng.integers(3)), int(rng.integers(2)))
        for step in range(12):
            a = int(rng.integers(4)) if rng.random() < EPSILON else int(q[s].argmax())
            ns, reward, done = transition(s,a,rng)
            update(q,s,a,reward,ns,done or step == 11)
            s=ns
            if done:
                break
    return q


def compare(q, episodes=200):
    results={}
    for name in ['Q-learning','Priority baseline']:
        rewards=[]
        for seed in range(10000,10000+episodes):
            rng=np.random.default_rng(seed)
            s=(int(rng.integers(2)),int(rng.integers(3)),int(rng.integers(2)))
            total=0
            for _ in range(12):
                a=int(q[s].argmax()) if name=='Q-learning' else baseline(s)
                s,r,done=transition(s,a,rng)
                total+=r
                if done:
                    break
            rewards.append(total)
        results[name]={'mean_reward':float(np.mean(rewards)), 'std_reward':float(np.std(rewards)), 'episodes':episodes}
    return results


def recommend(q, level, score, prerequisite):
    s=state(level,score,prerequisite)
    return {'state':s,'action':ACTIONS[int(q[s].argmax())], 'baseline':ACTIONS[baseline(s)], 'q_values':dict(zip(ACTIONS,q[s].tolist()))}
