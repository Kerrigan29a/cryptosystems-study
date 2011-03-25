#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that manages information about the language through a JSON file

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

import json


class LangNotFoundError(Exception):
    """
    Rises when there is no information about a particular language.
    Empty implementation.
    """
    pass


class LangsDB(object):
    """
    Handles the data stored on all the languages.
    """
    
    def __init__(self, fp):
        """
        ARGUMENT NOTES:
        fp -- file object
        """
        self.__langs = json.load(fp)

    @property
    def langs(self):
        """
        Return a list with all available languages
        """
        return self.__langs.keys()
    
    def kappa_index_of_coincidence(self, lang):
        """
        Return the 'kappa IC' of a language.
        If the given language is not found a LangNotFoundError will be raised.
        """
        lang_data = None
        try:
            lang_data = self.__langs[lang]
        except KeyError:
            raise LangNotFoundError
        
        try:
            return lang_data['kappa_IC']
        except KeyError:
            return 0

    
    def freqs(self, lang):
        """
        Return the 'kappa IC' of a language.
        If the given language is not found a LangNotFoundError will be raised.
        """
        lang_data = None
        try:
            lang_data = self.__langs[lang]
        except KeyError:
            raise LangNotFoundError
        
        try:
            freqs = lang_data['freqs']
            for char in freqs:
                if isinstance(freqs[char], basestring):
                    tmp_char = freqs[char]
                    freqs[char] = freqs[tmp_char]
            return freqs
        except KeyError:
            return None

    
    def __str__(self):
        new_freqs = dict()
        for lang in self.__langs.iterkeys():
            new_freqs = dict()
            for letter, freq in self.__langs[lang]['freqs'].iteritems():
                if not freq or freq == 0.0:
                    continue
                new_freqs[letter] = freq
            self.__langs[lang]['freqs'] = new_freqs
        return json.dumps(self.__langs, indent = 2, sort_keys=True)


if __name__=='__main__':
    
    import sys
    from pprint import pprint
    
    if len(sys.argv) < 2:
        print "USAGE:", sys.argv[0], "<json_file>"
    else:
        with open(sys.argv[1], "r") as fp:
            langs = LangsDB(fp)
        print langs

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
