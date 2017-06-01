#! /usr/bin/python -u

import os, sys, pickle, random, glob, gzip
import argparse as ap
import numpy as np
import matplotlib.pyplot as plt
import math

    
def get_targets(window, target_user):
    ''' Returns a list of users by how recent their last message is '''
    targets = []
    for m in window[::-1]:
        if m[1] not in targets and m[1] != target_user:
            targets.append(m)
    return targets

def get_weigths(targets, strategy = 'dumb'):
    # If only one user in window, he gets 100%
    # If two users, first gets 60%, other 40%
    # If three or more users, first gets 60%, second 30%, third 10%
    if strategy == 'dumb':
        if len(targets) == 0:
            return []
        else:
            return [(targets[0][1], 1.0)]
    elif strategy == 'spread':
        weigths = distrib_spread(len(targets))
        return [(targets[i][1], weigths[i]) for i in range(len(weigths))]
    elif strategy == 'cyril':
        weigths = distrib_cyril(len(targets))
        return [(targets[i][1], weigths[i]) for i in range(len(weigths))]


def distrib_spread(n, a = 1.0, r = .4):
    if n == 0:
        return []
    if n == 1:
        return [a]
    if n == 2:
        return [a * ( 1 - r ) , a * r]
    return [a * (1-r)] + distrib_spread(n-1, a*r, r)

def calc_lim(r):
    return (1-r)/(r*(2-r))

def distrib_cyril(n, p = .5, r = 0.4):
    if n == 0:
        return []
    limit = calc_lim(r) - 0.01
    if p > limit:
        p = limit
    tableau = [1.0]
    while n != 1:
        newT = list(tableau) 
        last = newT[-1]
        ponction = last*p
        s = len(tableau)
        pp = 0
        tableau = []
        for e in newT:
            if s-1 != len(tableau):
                tableau += [e * (1 - ponction)]
                pp += e * ponction
            else:
                tableau += [(e + pp) * (1 - r), (e + pp) * r]
        n -= 1
    return tableau


    pass

def _(f):
    return ["%0.4f" % e for e in f]

if __name__ == '__main__':
    p = ap.ArgumentParser()
    p.add_argument("n", type = int)
    p.add_argument("-p", type = float, default = 0.5)
    p.add_argument("-r", type = float, default = 0.4)
    args = p.parse_args()

    print sum(distrib_spread(args.n, r = args.r)), _(distrib_spread(args.n, r = args.r))
    print sum(distrib_cyril(args.n, args.p, args.r)), _(distrib_cyril(args.n, args.p, args.r))

    t1 = distrib_spread(args.n, r = args.r)
    t2 = distrib_cyril(args.n, args.p, args.r)

    plt.plot(t1)
    plt.plot(t2)
    plt.show()

# limite max de p est " (1 - r) / r*( 2 - r ) "







