#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: yhf
# @Date:   2015-04-20 18:18:45
# @Last Modified by:   yhf
# @Last Modified time: 2015-04-21 16:32:59


class TemplateError(Exception):
    pass


class TemplateContextError(TemplateError):

    def __init__(self, context_var):
        self.context_var = context_var

    def __str__(self):
        return "Cannot resolve '%s'." % self.context_var


class TemplateSyntaxError(TemplateError):

    def __init__(self, error_syntax):
        self.error_syntax = error_syntax

    def __str__(self):
        return "'%s' seems like invalid syntax." % self.error_syntax


class TemplateOperatorError(TemplateError):

    def __init__(self, error_op):
        self.error_op = error_op

    def __str__(self):
        return "'%s' is an invalid operator." % self.error_op
