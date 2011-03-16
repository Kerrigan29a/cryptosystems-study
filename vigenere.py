#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2011 Javier Escalada Gómez
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of copyright holders nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# ''AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL COPYRIGHT HOLDERS OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# Original Vigenère cypher and decypher from:
# http://codesnippets.joyent.com/posts/show/803

import string

def vigenere(c,k,e=1):
    """
    e=1 to encrypt
    e=-1 to decrypt

    >>> vigenere('thiscryptosystemisnotsecure', 'cipher')
    VPXZGIAXIVWPUBTTMJPWIZITWZT
    >>> vigenere('VPXZGIAXIVWPUBTTMJPWIZITWZT', 'cipher', -1)
    THISCRYPTOSYSTEMISNOTSECURE
    """

    wk=[string.ascii_uppercase.find(ch) for ch in k.upper()]
    wc=[string.ascii_uppercase.find(ch) for ch in c.upper()]


    wc = [ (x[0]+(e*x[1]))%26 for x in zip(wc,wk*(len(wc)/len(wk)+1))]

    return string.join([string.ascii_uppercase[x] for x in wc],"")


###
# KASISKI TEST
###

def _extract_group(c_text, i, j, min_group_len):
    old_i, old_j = i, j
    group = ""
    while c_text[i] == c_text[j]:
        group += c_text[i]
        i += 1
        j += 1
        if i >= len(c_text) or j >= len(c_text):
            break
    if not group or len(group) < min_group_len:
        return None
    else:
        return (old_i, old_j, group)

def factors(num):
    factors = []
    for i in xrange(1, num + 1):
        for j in xrange(i, num + 1):
            if i*j == num:
                factors.append(i)
                factors.append(j)
                break
            elif i*j > num:
                if i == j:
                    return factors
                break
    return factors

def kasiski_test(c_text, min_group_len=3):
    """ Kasiski test
    Return: List of tuples (key_len, frequency)
    """
    coincidences = []
    for i in xrange(len(c_text)):
        for j in xrange(i+1,len(c_text)):
            if c_text[i] == c_text[j]:
                coinc = _extract_group(c_text, i, j, min_group_len)
                if coinc:
                    coincidence = dict()
                    coincidence['factors'] = set(factors(coinc[1]-coinc[0]))
                    coincidence['group_len'] = len(coinc[2])
                    coincidences.append(coincidence)
    if not coincidences:
        return []

    coincidences = sorted(coincidences, key=lambda x: x['group_len'],
        reverse=True)
     
    group_max_len = coincidences[0]['group_len']
    lengths = []
    for i in xrange(3, group_max_len + 1):
        l_factors = [x['factors'] for x in
            filter(lambda x: x['group_len'] >= i, coincidences)]

        lengths += list(reduce(lambda x, y: x & y, l_factors))

    return [(key_len, float(lengths.count(key_len)) * 100 / len(lengths))
        for key_len in set(lengths)]

def print_kasiski_conclusions(data, verbose = False):
    print "===[Kasiski]==="
    sorted_data = sorted(data, key=lambda x: x[-1], reverse = True)
    if verbose:
        for (key_len, freq) in sorted_data:
            print "{0}: {1}%".format(key_len, freq)
        print "Conclusions:"
    i = 0
    if sorted_data[0][0] == 1:
       i = 1
    print "{0}: {1}%".format(sorted_data[i][0], sorted_data[i][-1])
    print "{0}: {1}%".format(sorted_data[i+1][0], sorted_data[i+1][-1])

###
# FRIEDMAN TEST
###

def delta_index_of_coincidence(columns):
    """Calculates 'Delta index of coincidence' (probability that a randomly
    chosen pair of letters in the message are equal).
    Columns must follow the following pattern:
[[('H', 'I', 'V', 'D', 'R', 'H', 'H'),
  ('F', 'C', 'W', 'B', 'T', 'U', 'Z'),
  ('C', 'O', 'C', 'L', 'I', 'K', 'W')],
  [...], ... , [...]]
    """
    num_of_chars_in_alphabet = 26
    acumulator = 0.0
    for column in columns:
        column = map(lambda x: ord(x) - 64, column) # 'A' = 1, 'B' = 2, ....
        list_n = [column.count(c) for c in xrange(1, num_of_chars_in_alphabet + 1)]
        summatory = reduce(lambda s, x: s + x * (x - 1), list_n, 0)
        N = len(column)
        acumulator += float(summatory) / (float(N * (N - 1)) / num_of_chars_in_alphabet)
    
    return acumulator / len(columns)

def friedman_test(c_text, min_len=3, max_len=50):
    columns = []
    max_len = min(max_len, len(c_text))
    for i in xrange(min_len, max_len):
        last_pos = 0
        row = []
        for j in xrange(0, len(c_text), i):
            j += i
            tmp_row = c_text[last_pos:j]
            if len(tmp_row) != i:
                tmp_row += (i - len(tmp_row)) * '@'
            row.append(tmp_row)
            last_pos = j
        delta_ic = delta_index_of_coincidence(zip(*row))
        columns.append((i, delta_ic))
    return columns

def print_friedman_conclusions(data, lang, lang_ic, verbose = False):
    print "===[Friedman]==="
    print "Lang of text: {0} (kappa I.C. = {1})".format(lang, lang_ic)
    friedman_data = data
    if verbose:
        for k, d in friedman_data:
            print "{0}: {1} ".format(k, d)
        print "Conclusions:"
    friedman_data_deltas = map(lambda t: (t[0], t[-1] - lang_ic), friedman_data)
    pos_deltas = filter(lambda t: t[-1] >= 0, friedman_data_deltas)
    neg_deltas = filter(lambda t: t[-1] < 0, friedman_data_deltas)
    if pos_deltas:
        min_pos = min(pos_deltas, key=lambda x: x[-1])
        print "{0}: {1} ({2})".format(min_pos[0], min_pos[-1] + lang_ic,  min_pos[-1])
    if neg_deltas:
        max_neg = max(neg_deltas, key=lambda x: x[-1])
        print "{0}: {1} ({2})".format(max_neg[0], max_neg[-1] + lang_ic,  max_neg[-1])


###
# MAIN
###
_lang = {
    #'lang': (index_of_coincidence, num_of_chars_in_alphabet)
    'English': (1.73, 26),
    'French': (2.02, 26),
    'German': (2.05, 30),
    'Italian': (1.94, 26),
    'Portuguese': (1.94, 26),
    'Russian': (1.76, 33), # Cyrillic alphabet
    'Spanish': (1.94, 27)
}

if __name__=='__main__':
    import sys

    if len(sys.argv) < 3 or sys.argv[1] not in ['ENCRYPT', 'DECRYPT', 'ANALYZE']:
        print "USAGE:", sys.argv[0]
        print "  DECRYPT <key>"
        print "  ENCRYPT <key>"
        print "  ANALYZE <lang>"
    else:
        text = ""
        for line in sys.stdin:
            text += line.strip()
        if sys.argv[1] == 'ANALYZE':
            print_kasiski_conclusions(kasiski_test(text))
            try:
                print_friedman_conclusions(friedman_test(text), sys.argv[2], _lang[sys.argv[2]][0])
            except KeyError:
                print "Unknown language. Known languages are:", ', '.join(_lang.keys())
        else:
            mode = 1
            if sys.argv[1] == 'DECRYPT':
                mode = -1
            c_text = vigenere(text, sys.argv[2], mode)
            print c_text
            
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 
