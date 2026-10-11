# Strategy: build a small model of each known style of opponent (fixed cycle,
# "beat your last move", "beat your most frequent recent move", and
# "second-order Markov on your moves"), keep score of which model has been
# predicting the opponent correctly, and play the move that beats the
# best-scoring model's prediction. If no model fits (e.g. a random opponent),
# fall back to random play.

import random

# BEATS[x] is the move that beats x
BEATS = {'R': 'P', 'P': 'S', 'S': 'R'}
QUINCY_CYCLE = ['R', 'R', 'P', 'P', 'S']
MODELS = ['quincy', 'kris', 'mrugesh', 'abbey']


def _new_state():
    return {
        'me': [],                      # my moves so far
        'hits': {m: 0 for m in MODELS},
        'pending': {},                 # each model's prediction for the current round
        'pairs': {a + b: 0 for a in 'RPS' for b in 'RPS'},
        'last': 'R',                   # last move in the abbey-style history
        'rounds': 0,
    }


def _predict_quincy(state):
    return QUINCY_CYCLE[(len(state['me']) + 1) % 5]


def _predict_kris(state):
    last = state['me'][-1] if state['me'] else 'R'
    return BEATS[last]


def _predict_mrugesh(state):
    last_ten = (['']+ state['me'])[-10:]
    most_frequent = max(['', 'R', 'P', 'S'], key=last_ten.count)
    if most_frequent == '':
        most_frequent = 'S'
    return BEATS[most_frequent]


def _predict_abbey(state):
    prev = state['last']
    options = [prev + 'R', prev + 'P', prev + 'S']
    best = max(options, key=lambda k: state['pairs'][k])
    return BEATS[best[-1]]


PREDICTORS = {
    'quincy': _predict_quincy,
    'kris': _predict_kris,
    'mrugesh': _predict_mrugesh,
    'abbey': _predict_abbey,
}


def player(prev_play, state=[None]):
    # An empty prev_play marks the first game of a new match: reset state.
    if prev_play == '' or state[0] is None:
        state[0] = _new_state()
    s = state[0]

    # Score each model on how well it predicted the opponent's last move.
    if prev_play:
        for name in MODELS:
            if s['pending'].get(name) == prev_play:
                s['hits'][name] += 1
        s['rounds'] += 1

    # Each model predicts the opponent's next move.
    s['pending'] = {name: PREDICTORS[name](s) for name in MODELS}

    # Follow the best model, unless none of them fits well.
    best = max(MODELS, key=lambda m: s['hits'][m])
    if s['rounds'] >= 20 and s['hits'][best] < 0.5 * s['rounds']:
        move = random.choice(['R', 'P', 'S'])
    else:
        move = BEATS[s['pending'][best]]

    # Record my move (and update the abbey-style pair counts).
    s['pairs'][s['last'] + move] += 1
    s['last'] = move
    s['me'].append(move)
    return move