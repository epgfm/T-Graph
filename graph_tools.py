#! /usr/bin/env python

import os, glob, shutil, string, pickle, gzip
import igraph
from distrib import *
import matplotlib.pyplot as plt
from igraph.drawing import *

import json
from misc import *


def build_graph(rows, window, distrib):
    g = igraph.Graph()
    g['vnames'] = set()
    for i in range(len(rows)-1):
        # Fixed-length window of messages before to update the edges
        w_start = i - window
        if w_start < 0:
            w_start = 0
        w = rows[w_start : i]
        target_date, target_uid, target_message = rows[i]
        # Check if message author in the graph, else add him.
        if target_uid not in g['vnames']:
            g.add_vertex(name=str(target_uid))
            g['vnames'].add(target_uid)
        target_vertex = g.vs.find(name=str(target_uid))
        weights = get_weigths(get_targets(w, target_uid), strategy = distrib)
        for to, weight in weights:
            v_to = g.vs.find(name=str(to))
            eid = g.get_eid(target_vertex, v_to, directed=False, error=False)
            if eid == -1: # edge does not exist
                g.add_edges([(target_vertex, v_to)])    # add it
                eid = g.get_eid(target_vertex, v_to, directed=False, error=False)
                g.es[eid]["weight"] = weight # and specify the weight
            else:
                g.es[eid]["weight"] += weight
    return g





def format_json(rows, label, raw_message, source):
    cur = get_database_cursor("so_bigbang")
    out = {}
    out_rows = []
    uid_names_dict = {}
    i = 0
    for r in rows:
        print "row: [%s]" % i, r
        i += 1
        date, uid, msg = r
        name = get_ircslug_from_uid(cur, uid)
        try:
            msg = msg.decode("utf-8")
        except:
            try:
                msg = msg.decode("latin-1")
            except:
                msg = "" + msg
        msg = "%s <%s> %s" % (date, name[0], msg)
        out_rows.append(msg)
        if uid not in uid_names_dict:
            uid_names_dict[uid] = name
    out['rows'] = out_rows
    out['channel'] = source
    out['uid_names_dict'] = uid_names_dict
    jsondata = json.dumps(out, sort_keys=True, indent=4, separators=(',', ': '))
    return jsondata




if __name__ == "__main__":
    import doctest
    doctest.testmod()




