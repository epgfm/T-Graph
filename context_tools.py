#! /usr/bin/env python
# coding: utf-8


import os, glob, shutil, string, pickle, gzip
import datetime, time


def split_raw_message(raw_message):
    ''' (message) -> (t, uid, type, text)
    '''
    text = raw_message[-1]
    mtype = raw_message[-2]
    if raw_message[2] == 'message':
        if raw_message[0] > 1400000000:
            return raw_message[0], raw_message[1], mtype, text
        return raw_message[1], raw_message[0], mtype, text
    elif raw_message[2] == 'chatMessage':
        return raw_message[0], raw_message[1], mtype, text



def get_message_context(message, cur):
    ''' (message with metadata) -> List of messages
    '''
    print "Hit get_message_context"
    # Parse the date and extract YYMMDD.
    t, uid, mtype, text = split_raw_message(message)
    # Get discussion id
    q = "select discussion_id from messages where messages.from like '%s' and date like '%s'" % (uid, t)
    print q
    cur.execute(q)
    res = cur.fetchall()
    if len(res) == 0:
        return [], [], None
    d_id = res[0][0]
    print "discussion_id: ", d_id
    # Now get the actual discussion, in chronological order
    q = ("select date, messages.from, content from messages where discussion_id like '%s' order by date" % d_id)
    print q
    cur.execute(q)
    res = cur.fetchall()
    rows = []
    for row in res:
        rows.append(row)
    rows.sort()

    i = 0
    for row in rows:
        c_t, c_uid, c_text = row
        if c_uid == uid and c_t == t: # OH JESUS FUCK
            break
        i += 1
    print rows[i]
    return rows[:i][-100:], rows[i+1 : i+101], d_id



def get_chatMessage_context(message, cur):
    ''' (message with metadata) -> List of messages
    '''
    print "Hit get_chatMessage_context"
    # Parse the date and extract YYMMDD.
    t, uid, mtype, text = split_raw_message(message)
    print type(text)

    t = datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')

    try:
        text = "%" + text.decode("UTF-8") + "%"
    except:
        text = "%" + text.decode("latin-1").encode("utf-8") + "%"

    # Extract target record from the table
    q = "select * from chatMessages where uid like %s and message like %s"
    print q, (uid, text)
    cur.execute(q, (uid, "%" + text + "%"))
    res = cur.fetchall()
    if len(res) < 1:
        print "get_chatMessage_context [FAIL]LOCATE/"
        text = "%".join(text.split())
        q = "select * from chatMessages where uid like %s and message like %s"
        print q, (uid, text)
        cur.execute(q, (uid, "%" + text + "%"))
        res = cur.fetchall()
        if len(res) < 1:
            with open("locate_errs.txt", "a+") as f:
                print >> f, "get_chatMessage_context [FAIL]MULTIPLELOCATE/"
                print >> f, q, (uid, text)
            return [], [], None

    t, uid, chan, message, mid = res[0]
    print "get_chatMessage_context LOCATE/", res[0]
    q = "select * from chatMessages where date < '%s' and chan like '%s' order by date DESC limit 100" % (t, chan)
    print q
    cur.execute(q)
    pre = cur.fetchall()
    pre = list(pre)
    pre.sort()
    q = "select * from chatMessages where date > '%s' and chan like '%s' order by date limit 100" % (t, chan)
    print q
    cur.execute(q)
    post = cur.fetchall()
    return pre, post, chan
    



def normalize_context(context):
    ''' (context) -> context

    Normalize context depending on the message type
    The goal is to return context in a consistent format.
    No matter the message type output of this function is
    pre, target_message, post
    Messages in pre and post are time, uid, msg with time format f.
    target_message is also in that format so we can concatenate all elements
    of the return tuple to get the history.

    '''
    f = '%Y-%m-%d/%H:%M:%S'
    pre, target, post, source = context
    if target[2] == 'message':
        t_uid, t_time, t_message = target[0], target[1], target[3]
        target_out = (time.strftime(f, time.localtime(t_time)), t_uid, t_message)
        pre_out = []
        for row in pre:
            t, u, m = row
            t = time.strftime(f, time.localtime(t))
            pre_out.append((t, u, m))
        post_out = []
        for row in post:
            t, u, m = row
            t = time.strftime(f, time.localtime(t))
            post_out.append((t, u, m))
    else:
        t_uid, t_time, t_message = target[1], target[0], target[3]
        target_out = (time.strftime(f, time.localtime(t_time)), t_uid, t_message)
        pre_out = []
        for row in pre:
            u, t, m = row[1], row[0], row[3]
            t = t.strftime(f)
            pre_out.append((t, u, m))
        post_out = []
        for row in post:
            u, t, m = row[1], row[0], row[3]
            t = t.strftime(f)
            post_out.append((t, u, m))
    return (pre_out, target_out, post_out, source)









