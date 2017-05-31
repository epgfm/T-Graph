#! /usr/bin/python -u

import os, sys, pickle, random, glob, gzip, time
import datetime
import argparse as ap
import MySQLdb
from misc import *

from context_tools import *

'''

    This program does an information gathering pass on our corpus and gather
    extra data for each message.

'''


def comments_from_file(fileName):
    ''' Load and return messages in fileName '''
    content = zload(fileName)
    comments = [c for c in content]
    return comments



def load_full_comments(p):
    X, y = [], []
    zerosFile = glob.glob("10-Split/*0.*-%s*" % p)[0]
    zeros = comments_from_file(zerosFile)
    onesFile = glob.glob("10-Split/*1.*-%s*" % p)[0]
    ones = comments_from_file(onesFile)
    y.extend([0 for v in range(len(zeros))])
    y.extend([1 for v in range(len(ones))])
    X.extend(zeros)
    X.extend(ones)
    return X, y





def extract_message_data(c, curbang):
    t, uid, mtype, text = split_raw_message(c)
    pre, post = get_message_context(c, curbang)
    return pre, c, post



def extract_chatMessage_data(c, curtry):
    t, uid, mtype, text = split_raw_message(c)
    pre, post = get_chatMessage_context(c, curtry)
    return pre, c, post



def extract_data(c, curtry, curbang):
    if c[2] == "message":
        return extract_message_data(c, curbang)
    else:
        return extract_chatMessage_data(c, curtry)



if __name__ == '__main__':

    # Establish the needed database connections
    dbtry = MySQLdb.connect(host = "localhost", user = "ouroumov",
                            passwd = "lolwhat", db = "try",
                            charset='utf8')

    dbbang = MySQLdb.connect(host = "localhost", user = "ouroumov",
                             passwd = "lolwhat", db = "so_bigbang",
                             charset='utf8')

    # Get the database cursors
    curtry = dbtry.cursor()
    curbang = dbbang.cursor()


    for p in range(10):
        comments, labels = load_full_comments(p)
        extra_data = []
        for c in comments:
            print "==" * 80
            print "[TARGET]", c
            # Run extraction of extra data for both types.
            extra_datum = extract_data(c, curtry, curbang)
            pre, c, post = extra_datum
            for m in pre:
                print m
            print c
            for m in post:
                print m
            extra_data.append(extra_datum)
        zdump(extra_data, "context/extra-%s.pkl.gz" % p)



