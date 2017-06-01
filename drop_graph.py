#! /usr/bin/python -u

import os, sys, pickle, random, glob, gzip
import argparse as ap
from drop_context import load_full_comments
from context_tools import normalize_context
from graph_tools import *
from misc import *
import igraph
from distrib import *
import matplotlib.pyplot as plt
from igraph.drawing import *

'''
    Specs:
    Arguments: part + indice
    Drop graph for part/indice using the data in context and 10-Split

'''


def get_all_data(p, i):
    ''' (int, int) -> (raw_message, label, context)

    Get the data corresponding to part number p and indice i.

    '''
    # Load raw message
    comments, labels = load_full_comments(p)
    raw_message = comments[i]
    label = labels[i]

    # Load context
    part_context = zload("context/extra-%s.pkl.gz" % p)
    context = part_context[i]
    return raw_message, label, context







if __name__ == '__main__':

    p = ap.ArgumentParser()
    p.add_argument("part", type = int)
    p.add_argument("indice", type = int)
    args = p.parse_args()

    
    raw_message, label, context = get_all_data(args.part, args.indice)
    print raw_message
    print label
    print context[1]
    print context[0][0]

    # OK so now I have context, but I need to normalize it.
    context = normalize_context(context)

    pre, target, post, source = context
    for r in pre:
        print r
    printColor("red", target)
    for r in post:
        print r

    rows = list(pre) + [list(target)] + list(post)
    print "target", target
    print format_json(rows, label, raw_message, source)


    g = build_graph(rows, 10, 'cyril')
    print "Nodes:", len(g.vs), "Edges:", len(g.es)
    layout = g.layout("kk3d")

    fname = "%s_%s" % (args.part, args.indice) + ".graphml"

    g.save(fname)
    igraph.plot(g, "%s_%s_plot.pdf" % (args.part, args.indice))




