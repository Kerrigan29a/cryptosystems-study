#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A Implementation of the Vigenère cryptosystem and some tests to analyze it.

Original Vigenère cypher and decypher from:
http://codesnippets.joyent.com/posts/show/803

-----

Copyright (c) 2011 Javier Escalada Gómez
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
3. Neither the name of copyright holders nor the names of its
   contributors may be used to endorse or promote products derived
   from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
''AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL COPYRIGHT HOLDERS OR CONTRIBUTORS
BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""

import string


def vigenere(text,key,mode=1):
    """
    Vigènere algorithm to encrypt and decrypt some text

    ARGUMENT NOTES:
    mode -- 1 to encrypt or -1 to decrypt
    
    USAGE:
    >>> vigenere('thiscryptosystemisnotsecure', 'cipher')
    VPXZGIAXIVWPUBTTMJPWIZITWZT
    >>> vigenere('VPXZGIAXIVWPUBTTMJPWIZITWZT', 'cipher', -1)
    THISCRYPTOSYSTEMISNOTSECURE
    """

    wk=[string.ascii_uppercase.find(ch) for ch in key.upper()]
    wc=[string.ascii_uppercase.find(ch) for ch in text.upper()]

    wc = [ (x[0] + (mode * x[1])) % 26 for x in zip(wc, wk *(len(wc) / len(wk) + 1))]

    return string.join([string.ascii_uppercase[x] for x in wc], "")


###
# KASISKI TEST
###

def _extract_group(encr_text, fst_group_pos, snd_group_pos, min_group_len):
    """
    Extract the largest group of characters may match at each position

    ARGUMENT NOTES:
    min_group_len -- The min length of the group

    RETURN NOTES:
    If the group has no minimum size, None. Otherwise, the following tuple:
    (fst_group_pos, snd_group_pos, group_str)

    USAGE:
    >>> _extract_group('CSASTPKVSIQUTGQUCSASTPIUAQJB', 0, 16, 3)
    (0, 16, 'CSASTP')
    """
    
    old_fst_group_pos, old_snd_group_pos = fst_group_pos, snd_group_pos
    group = ""
    while encr_text[fst_group_pos] == encr_text[snd_group_pos]:
        group += encr_text[fst_group_pos]
        fst_group_pos += 1
        snd_group_pos += 1
        if fst_group_pos >= len(encr_text) or snd_group_pos >= len(encr_text):
            break
    if not group or len(group) < min_group_len:
        return None
    else:
        return (old_fst_group_pos, old_snd_group_pos, group)


def factors(num):
    """
    Extract all the factors of a number
    
    USAGE:
    >>> factors(264)
    [1, 264, 2, 132, 3, 88, 4, 66, 6, 44, 8, 33, 11, 24, 12, 22]
    """
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


def kasiski_test(encr_text, min_group_len=3):
    """
    The Kasiski examination allows a cryptanalyst to deduce the length of the
    keyword used in the polyalphabetic substitution cipher.
    
    For more info:
    http://en.wikipedia.org/wiki/Vigen%C3%A8re_cipher
    http://en.wikipedia.org/wiki/Kasiski_examination

    ARGUMENT NOTES:
    min_group_len -- The min length of the group

    RETURN NOTES:
    A list of tuples with he following format:
    (key_len, frequency)

    USAGE:
    >>> kasiski_test('CSASTPKVSIQUTGQUCSASTPIUAQJB')
    [(16, 20.0), (1, 20.0), (2, 20.0), (4, 20.0), (8, 20.0)]
    """
    coincidences = []
    for i in xrange(len(encr_text)):
        for j in xrange(i+1,len(encr_text)):
            if encr_text[i] == encr_text[j]:
                coinc = _extract_group(encr_text, i, j, min_group_len)
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
    """
    Analyzes the data to show a few conclusions from the test data.
    In verbose mode also shows the raw data.

    ARGUMENT NOTES:
    data -- Data returned from kasiski_test()
    """

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
    """
    Calculate 'delta index of coincidence' (probability that a randomly
    chosen pair of letters in the message are equal).

    USAGE:
    >>> delta_index_of_coincidence([('C', 'S', 'K', 'I', 'T', 'U', 'A', 'P', 'A', 'B'), ('S', 'T', 'V', 'Q', 'G', 'C', 'S', 'I', 'Q', '@'), ('A', 'P', 'S', 'U', 'Q', 'S', 'T', 'U', 'J', '@')])
    0.9629629629629628
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


def friedman_test(encr_text, min_len=3, max_len=50):
    """
    The Friedman test (sometimes known as the kappa test) uses the index of
    coincidence to guess the length of the key.

    For more info:
    http://en.wikipedia.org/wiki/Vigen%C3%A8re_cipher
    http://en.wikipedia.org/wiki/Index_of_coincidence

    ARGUMENT NOTES:
    min_group_len -- The min length of the group
    min_group_len -- The max length of the group
    
    RETURN NOTES:
    A list of tuples with he following format:
    (key_len, delta_index_of_coincidence)

    USAGE:
    >>> friedman_test('CSASTPKVSIQUTGQUCSASTPIUAQJB')
    [(3, 0.9629629629629628), (4, 3.7142857142857144), (5, 0.6933333333333334), (6, 1.2999999999999998), (7, 1.238095238095238), (8, 4.875), (9, 0.9629629629629629), (10, 0.0), (11, 2.3636363636363638), (12, 0.7222222222222222), (13, 0.6666666666666666), (14, 1.8571428571428572), (15, 1.7333333333333334), (16, 9.75), (17, 0.0), (18, 1.4444444444444444), (19, 0.0), (20, 0.0), (21, 0.0), (22, 1.1818181818181819), (23, 0.0), (24, 0.0), (25, 0.0), (26, 0.0), (27, 0.0)]
    """
    columns = []
    max_len = min(max_len, len(encr_text))
    for i in xrange(min_len, max_len):
        last_pos = 0
        row = []
        for j in xrange(0, len(encr_text), i):
            j += i
            tmp_row = encr_text[last_pos:j]
            if len(tmp_row) != i:
                tmp_row += (i - len(tmp_row)) * '@'
            row.append(tmp_row)
            last_pos = j
        delta_ic = delta_index_of_coincidence(zip(*row))
        columns.append((i, delta_ic))
    return columns


def print_friedman_conclusions(data, lang, lang_ic, verbose = False):
    """
    Analyzes the data to show a few conclusions from the test data.
    In verbose mode also shows the raw data.

    ARGUMENT NOTES:
    data -- Data returned from friedman_test()
    lang -- The name of the language in which it is assumed that the text is
        written.
    lang_ic -- The ' kappa index of coincidence' of the language in which it is
        assumed that the text is written
    """

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
            encr_text = vigenere(text, sys.argv[2], mode)
            print encr_text
            
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 
