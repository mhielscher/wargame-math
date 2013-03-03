#!/usr/bin/python

# (((range, attack, damage), ...), target_score)



weapons = {
    "16-pound Cannon":
        {"range": [2,5,8,11,14],
         "attack": [4,2,0,-2,-4],
         "damage": {(1,2): [2,1,1,1,1],
                    (3,4): [3,2,2,2,1],
                    (5,6): [4,3,2,2,1],
                    (7,8): [5,4,2,2,1],
                    (9,0): [6,5,3,3,1]
                   },
         "points": 2
        },
    "16-pound Carronade":
        {"range": [1,2,4,5,7],
         "attack": [4,2,0,-2,-4],
         "damage": {(1,2): [3,2,1,1,1],
                    (3,4): [5,3,2,2,1],
                    (5,6): [6,4,3,2,1],
                    (7,8): [7,5,4,2,1],
                    (9,0): [9,6,5,3,1]
                   },
         "points": 1
        },
    "16-pound Culverin":
        {"range": [4,8,12,16,21],
         "attack": [4,2,0,-2,-4],
         "damage": {(1,2): [1,1,1,1,1],
                    (3,4): [2,2,2,1,1],
                    (5,6): [3,2,2,1,1],
                    (7,8): [4,2,2,1,1],
                    (9,0): [5,3,3,1,1]
                   },
         "points": 2
        },
    "16-pound Mortar":
        {"range": [2,5,8,11,14],
         "attack": [2,1,-1,-3,-4],
         "damage": {(1,2): [2,2,1,1,1],
                    (3,4): [4,3,2,2,1],
                    (5,6): [5,4,3,2,1],
                    (7,8): [6,5,4,2,1],
                    (9,0): [8,6,5,3,1]
                   },
         "points": 2
        },
    "16-pound Howitzer":
        {"range": [2,5,8,11,14],
         "attack": [6,3,1,-1,-4],
         "damage": {(1,2): [1,1,1,1,1],
                    (3,4): [2,2,2,1,1],
                    (5,6): [3,2,2,1,1],
                    (7,8): [4,2,2,1,1],
                    (9,0): [5,3,3,1,1]
                   },
         "points": 1.5
        }
}

#transpose
weapons_columns = {name: zip(d['range'], d['attack'], *(dmg[1] for dmg in sorted(d['damage'].items()))) for name, d in weapons.items()}


def score(data):
    total = 0
    for 
    return 0

def fitness(data, target):
    return abs(score(data) - target);


