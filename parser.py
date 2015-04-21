#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: yhf
# @Date:   2015-04-20 18:06:16
# @Last Modified by:   yhf
# @Last Modified time: 2015-04-21 16:50:19


import operator
import ast

from tokenizer import WHITESPACE_REGEX, OPERATOR_DICT
from error import TemplateError, TemplateSyntaxError, TemplateContextError, TemplateOperatorError


def eval_expr(expr):
    """Evaluates an expression node.

    To check they are literals or context variables,
    use ast.leteral_eval to safely evaluate strings.
    """
    try:
        return 'literal', ast.literal_eval(expr)
    except ValueError, SyntaxError:
        return 'name', expr


def resolve(name, context):
    """Handles a context variable name.

    Search for its value in the context.
    Need to handle dotted names.
    """
    if name.startswith('..'):
        context = context.get('..', {})
        name = name[2:]
    try:
        for token in name.split('.'):
            context = context[token]
        return context
    except KeyError:
        raise TemplateContextError(name)


class _Node(object):

    creates_scope = False

    def __init__(self, fragment=None):
        self.children = []
        self.process_fragment(fragment)

    def process_fragment(self, fragment):
        """Processes fragment contents and store attributes on Node objects.
        """
        pass

    def render(self, context):
        """Converts Node object to HTML using the provided context.
        """
        pass

    def enter_scope(self):
        pass

    def exit_scope(self):
        pass

    def render_children(self, context, children=None):
        if children is None:
            children = self.children

        def render_child(child):
            child_html = child.render(context)
            return '' if not child_html else str(child_html)

        return ''.join(map(render_child, children))


class _ScopableNode(_Node):

    creates_scope = True


class _Root(_Node):

    def render(self, context):
        return self.render_children(context)


class _Variable(_Node):
    """
    Sample:
    {% each articles %}
        <ul>itere.title</ul>
    {% end %}
    """

    def process_fragment(self, fragment):
        self.name = fragment

    def render(self, context):
        return resolve(self.name, context)


class _Each(_ScopableNode):
    """
    Sample:
    {% each articles %}
        <li>iter.title</li>
    {% end %}

    {% each [1, 2, 3] %}
        <li>{{ iter }}</li>
    {% end %}

    {% each records %}
        <li>{{ ..name }}</li>
    {% end %}
    """

    def process_fragment(self, fragment):
        try:
            _, iter = WHITESPACE_REGEX.split(fragment, 1)
            self.iter = eval_expr(iter)
        except ValueError:
            raise TemplateSyntaxError(fragment)

    def render(self, context):
        items = self.iter[1] if self.iter[0] == 'literal' else resolve(self.iter[1], context)
        def render_item(item):
            return self.render_children({'..': context, 'iter': item})
        return ''.join(map(render_item, items))


class _If(_ScopableNode):
    """
    Sample:
    {% if x > 1 %}
        ......
    {% else %}
        ......
    {% end %}
    """

    def process_fragment(self, fragment):
        bits = fragment.split()[1:]
        if len(bits) not in (1, 3):
            raise TemplateSyntaxError(fragment)

        self.lhs = eval_expr(bits[0])
        if len(bits) == 3:
            self.op = bits[1]
            self.rhs = eval_expr(bits[2])

    def render(self, context):
        lhs = self.resolve_side(self.lhs, context)
        if hasattr(self, 'op'):
            op = OPERATOR_DICT.get(self.op)
            if op is None:
                raise TemplateOperatorError(self.op)
            rhs = self.resolve_side(self.rhs, context)
            exec_if_branch = op(lhs, rhs)
        else:
            exec_if_branch = operator.truth(lhs)
        if_branch, else_branch = self.split_children()
        return self.render_children(context,
            self.if_branch if exec_if_branch else self.else_branch)

    def resolve_side(self, side, context):
        return side[1] if side[0] == 'literal' else resolve(side[1], context)

    def exit_scope(self):
        self.if_branch, self.else_branch = self.split_children()

    def split_children(self):
        if_branch, else_branch = [], []
        curr = if_branch
        for child in self.children:
            if isinstance(child, _Else):
                curr = else_branch
                continue
            curr.append(child)
        return if_branch, else_branch


class _Else(_Node):

    def render(self, context):
        pass


class _Call(_Node):
    """
    Sample:
    def pow(m=2, e=2):
        return m ** e

    {% call pow %}
    {% call pow 3 4 %}
    """

    def process_fragment(self, fragment):
        try:
            bits = WHITESPACE_REGEX.split(fragment)
            self.callable = bits[1]
            self.args, self.kwargs = self._parse_params(bits[2:])
        except ValueError, IndexError:
            raise TemplateSyntaxError(fragment)

    def _parse_params(self, params):
        args, kwargs = [], {}
        for param in params:
            if '=' in param:
                name, value = param.split('=')
                kwargs[name] = eval_expr(value)
            else:
                args.append(eval_expr(param))
        return args, kwargs

    def render(self, context):
        resolved_args, resolved_kwargs = [], {}
        for eval_type, eval_result in self.args:
            if eval_type == 'name':
                eval_result = resolve(eval_result, context)
            resolved_args.append(eval_result)

        for key, (eval_type, eval_result) in self.kwargs.items():
            if eval_type == 'name':
                eval_result = resolve(eval_result, context)
            resolved_kwargs[key] = eval_result

        resolved_callable = resolve(self.callable, context)
        if hasattr(resolved_callable, '__call__'):
            return resolved_callable(*resolved_args, **resolved_kwargs)
        else:
            raise TemplateError("'%s' is not callable" % self.callable)


class _Text(_Node):

    def process_fragment(self, fragment):
        self.text = fragment

    def render(self, context):
        return self.text
