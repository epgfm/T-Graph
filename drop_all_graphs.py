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


def get_sample_length(p):
    # Load raw message
    comments, labels = load_full_comments(p)
    return len(labels)


def drop_dir(p, i):
    if not os.path.isdir("GRAPHES/%s" % p):
        os.mkdir("GRAPHES/%s" % p)
    if os.path.isdir("GRAPHES/%s/%s" % (p, i)):
        shutil.rmtree("GRAPHES/%s/%s" % (p, i))
    os.mkdir("GRAPHES/%s/%s" % (p, i))




if __name__ == '__main__':

    for p in range(10):
        
        for i in range(get_sample_length(p)):

            raw_message, label, context = get_all_data(p, i)

            context = normalize_context(context)
            pre, target, post, source = context
            rows = list(pre) + [list(target)] + list(post)

            g = build_graph(rows, 10, 'cyril')
            print "Nodes:", len(g.vs), "Edges:", len(g.es)
            layout = g.layout("kk3d")

            fname = "GRAPHES/%s/%s/full" % (p, i) + ".graphml"

            g.save(fname)
            igraph.plot(g, "GRAPHES%s/%s/full.pdf" % (p, i))







