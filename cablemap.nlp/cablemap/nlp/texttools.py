# -*- coding: utf-8 -*-
#
# Copyright (c) 2011 - 2012 -- Lars Heuer <heuer[at]semagia.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#     * Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#
#     * Neither the project name nor the names of the contributors may be 
#       used to endorse or promote products derived from this software 
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
"""\
Text-related utilities to process the cable content.
"""
from __future__ import with_statement
import os
import re
import codecs
import string
import nltk
import gensim
from cablemap.core import reader

stop_words = set(nltk.corpus.stopwords.words('english'))
_tokenize = nltk.tokenize.WordPunctTokenizer().tokenize
_porter_stem = nltk.stem.PorterStemmer().stem
_lanc_stem = nltk.stem.LancasterStemmer().stem

_CLEAN_PATTERNS = (
        # pattern, substitution
        (re.compile(r'''([0-9]+\s*\.?\s*\(?[SBU/NTSC]+\)[ ]*)  # Something like 1. (C)
                    |(\-{3,}|={3,}|_{3,}|/{3,}|\#{3,}|\*{3,}|\.{3,})      # Section delimiters
                    |(\s*[A-Z]+\s+[0-9 \.]+OF\s+[0-9]+)    # Section numbers like ROME 0001 003.2 OF 004
                    |(^[0-9]+\s*\.\s*)                     # Paragraph numbering without classification
                    |((END )?\s*SUMMAR?Y(\s+AND\s+COMMENT)?(\s+AND\s+ACTION\s+REQUEST)?\s*\.?:?[ ]*) # Introduction/end of summary
                    |((END )?\s*COMMENT\s*\.?:?[ ]*)       # Introduction/end of comment
                    |(^\s*SIPDIS\s*)                       # Trends to occur randomly ;)
                    ''', re.VERBOSE|re.MULTILINE|re.IGNORECASE),
            ''),
    )

def clean_cable_content(content):
    """\
    Removes content like "1. (C)" from the content.
    
    `content`
        The content of the cable.
    """
    for pattern, subst in _CLEAN_PATTERNS:
        content = pattern.sub(subst, content)
    return content


_UNWANTED_WORDS_PATTERN = re.compile(ur'--+|xx+|^[ %s”’]+$' % string.punctuation, re.IGNORECASE|re.UNICODE)

def words(content, filter=True, predicate=None):
    """\
    Returns an iterable of words from the provided text.
    
    `content`
        A text.
    `filter`
        Indicates if stop words and garbage like "xxxxxx" should be removed from
        the word list.
    `predicate`
        An alternative word filter. If it is ``None`` "xxxx", "---",
        default stop words, and words which have no min. length of 3 are filtered
        (iff ``filter`` is set to ``True``).
    
    >>> list(words('Hello and goodbye ------ '))
    ['Hello', 'goodbye']
    >>> list(words('Hello, and goodbye ------ Subject xxxxxxxxx XXXXXXXXXXXX here'))
    ['Hello', 'goodbye', 'Subject']
    >>> list(words('Hello, and goodbye.How are you?'))
    ['Hello', 'goodbye']
    """
    def accept_word(word):
        """\
        Returns if the `word` is acceptable/useful
        
        `word`
            The word to check.
        """
        return len(word) > 2 \
                and word.lower() not in stop_words \
                and not _UNWANTED_WORDS_PATTERN.match(word)
    words = _tokenize(content)
    if filter or predicate:
        if not predicate:
            predicate = accept_word
        return (w for w in words if predicate(w))
    return words

def lowercased_words(content, filter=True, predicate=None):
    """\
    Returns an iterable of lowercased words from the provided text.
    
    `content`
        A text.
    `filter`
        Indicates if stop words and garbage like "xxxxxx" should be removed from
        the word list.
    `predicate`
        An alternative word filter. If it is ``None`` "xxxx", "---",
        default stop words, and words which have no min. length of 3 are filtered
        (iff ``filter`` is set to ``True``).
    
    >>> list(lowercased_words('Hello and goodbye ------ '))
    ['hello', 'goodbye']
    >>> list(lowercased_words('Hello, and goodbye ------ Subject xxxxxxxxx XXXXXXXXXXXX here'))
    ['hello', 'goodbye', 'subject']
    >>> list(lowercased_words('Hello, and goodbye.How are you?'))
    ['hello', 'goodbye']
    """
    return (w.lower() for w in words(content, filter, predicate))

def sentence_list(content):
    """\
    Returns a list of sentences from the provided content.
    
    `content`
        A text.
    
    >>> sentence_list("I've been waiting. I've been waiting night and day.")
    ["I've been waiting.", "I've been waiting night and day."]
    """
    return nltk.sent_tokenize(content)

def porter_stem(word):
    """\
    Strips affixes from the word and returns the stem using the Porter stemming 
    algorithm.
    """
    return _porter_stem(word)

def lancaster_stem(word):
    """\
    Stems a word using the Lancaster stemming algorithm.
    """
    return _lanc_stem(word)

   
if __name__ == '__main__':
    import doctest
    doctest.testmod()
