#! /usr/bin/python -u

import os, sys, pickle, random, glob, gzip
import argparse as ap

'''
    Specs:
    Arguments: part + indice
    Drop graph for part/indice using the data in context and 10-Split

'''




if __name__ == '__main__':

    p = ap.ArgumentParser()
    p.add_argument("part", type = int)
    p.add_argument("indice", type = int)
    args = p.parse_args()

    

