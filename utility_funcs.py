#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Some utility functions to provide information about a text

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

import math

def freqs(text, relative = True, case_sensitive = False):
    """
    Calculate frequency of characters in a text.
    This function works internally with Unicode characters. The text passed as
    parameter will be converted if necessary.

    ARGUMENT NOTES:
    relative -- 'True' if the frequencies must be relative. 'False' in case the
        frequencies must be accumulated.
    case_sensitive -- If 'False ' all alphabetic characters are converted to
        lowercase

    USAGE:
    >>> freqs("HELLOwOrlD")
    {u'e': 0.1, u'd': 0.1, u'h': 0.1, u'l': 0.3, u'o': 0.2, u'r': 0.1, u'w': 0.1}
    """
    if not isinstance(text, unicode):
        text = text.decode('utf-8')
    
    n = dict()
    N = 0
    for char in text:
        if char.isalpha():
            if not case_sensitive:
                char = char.lower()
            try:
                n[char] += 1
            except KeyError:
                n[char] = 1
            finally:
                N += 1
    
    if relative:
        f = dict()
        for k, a in n.iteritems():
            f[k] = float(a)/N
        return f
    
    return n


def delta_index_of_coincidence(text, n, num_chars = 26, case_sensitive = False):
    """
    Calculate 'delta index of coincidence'.
    This function works internally with Unicode characters. The text passed as
    parameter will be converted if necessary.
    
    ARGUMENT NOTES:
    n -- Accumulated frequencies
    num_chars -- The number of possible different characters that can appear in
        the text
    case_sensitive -- If 'False ' all alphabetic characters are converted to
        lowercase

    USAGE:
    >>> text="HELLO WORLD"
    >>> delta_index_of_coincidence(text, freqs(text, relative = False))
    1.8909090909090909
    """

    if not isinstance(text, unicode):
        text = text.decode('utf-8')

    if not case_sensitive:
        text = map(lambda x: x.lower(), text)

    summatory = reduce(lambda s, x: s + x * (x - 1), n.itervalues(), 0)
    N = len(text)
    return float(summatory) / (float(N * (N - 1)) / num_chars)


def entropy(f, case_sensitive = False):
    """
    Calculate the amount of entropy.
    This function works internally with Unicode characters. The text passed as
    parameter will be converted if necessary.

    ARGUMENT NOTES:
    f -- Relative frequencies
    case_sensitive -- If 'False ' all alphabetic characters are converted to
        lowercase

    USAGE:
    >>> entropy(freqs("HELLO WORLD"))
    2.530857153109955
    """
    return reduce(lambda s, x: s + f[x] * math.log(f[x], 2), f.keys(), 0) * -1


if __name__=='__main__':
    
    import sys
    import json
    
    text = ""
    for line in sys.stdin:
        text += line.strip()
    print "Text:", text
    print ""
    print "Relative frequencies:", json.dumps(freqs(text), indent = 2, sort_keys=True)
    print ""
    print "Entropy:", entropy(freqs(text))
    print ""
    print "Delta index of coincidence:", delta_index_of_coincidence(text,
        freqs(text, relative = False))
 
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
