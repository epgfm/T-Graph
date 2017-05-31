#! /usr/bin/env python
# coding: utf-8


import os, glob, shutil, string, pickle, gzip
import datetime


def timestamp_to_date(ts):
    return 


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
        return [], []
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
        if c_uid == uid:
            break
        i += 1
    print rows[i]
    return rows[:i][-10:], rows[i+1 : i+11]



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
            return [], []



    t, uid, chan, message = res[0]
    print "get_chatMessage_context LOCATE/", res[0]
    q = "select * from chatMessages where date < '%s' and chan like '%s' order by date DESC limit 20" % (t, chan)
    print q
    cur.execute(q)
    pre = cur.fetchall()
    pre = list(pre)
    pre.sort()
    q = "select * from chatMessages where date > '%s' and chan like '%s' order by date limit 20" % (t, chan)
    print q
    cur.execute(q)
    post = cur.fetchall()
    return pre, post
    


if __name__ == "__main__":
    import doctest
    doctest.testmod()




