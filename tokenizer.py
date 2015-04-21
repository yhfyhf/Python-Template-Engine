#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: yhf
# @Date:   2015-04-20 18:03:07
# @Last Modified by:   yhf
# @Last Modified time: 2015-04-21 16:57:23


import re
import operator


VAR_FRAGMENT = 0
BLOCK_FRAGMENT_START = 1
BLOCK_FRAGMENT_END = 2
TEXT_FRAGMENT = 3

VAR_TOKEN_LEFT = '{{'
VAR_TOKEN_RIGHT = '}}'
BLOCK_TOKEN_LEFT = '{%'
BLOCK_TOKEN_RIGHT = '%}'


TOKEN_REGEX = re.compile(r'(%s.*?%s|%s.*?%s)' % (
    VAR_TOKEN_LEFT,
    VAR_TOKEN_RIGHT,
    BLOCK_TOKEN_LEFT,
    BLOCK_TOKEN_RIGHT,
))

WHITESPACE_REGEX = re.compile('\s+')

OPERATOR_DICT = {
    '>': operator.gt,
    '<': operator.lt,
    '==': operator.eq,
    '>=': operator.ge,
    '<=': operator.le,
    '!=': operator.ne,
}


def tokenize(string):
    for fragment in TOKEN_REGEX.split(string):
        if fragment:
            yield _Fragment(fragment)


class _Fragment(object):

    def __init__(self, raw_text):
        self.raw_text = raw_text
        self.clean_text = self.clean_fragment()

    def clean_fragment(self):
        """ Cleans fragments.

        Remove whitespaces on the two sides.
        If raw text starts with '{{' or '{%', then return text among,
        else return the text.
        """
        if self.raw_text[:2] in (VAR_TOKEN_LEFT, BLOCK_TOKEN_LEFT):
            return self.raw_text.strip()[2:-2].strip()
        return self.raw_text

    @property
    def type(self):
        raw_start = self.raw_text[:2]
        if raw_start == VAR_TOKEN_LEFT:
            return VAR_FRAGMENT
        elif raw_start == BLOCK_TOKEN_LEFT:
            return BLOCK_FRAGMENT_END if self.clean_text[:3] == 'end' else BLOCK_FRAGMENT_START
        else:
            return TEXT_FRAGMENT

    def __str__(self):
        return str((self.clean_text, self.type))
