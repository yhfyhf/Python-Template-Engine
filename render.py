#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: yhf
# @Date:   2015-04-20 18:23:27
# @Last Modified by:   yhf
# @Last Modified time: 2015-04-21 16:59:04


from tokenizer import TOKEN_REGEX, _Fragment
from parser import _Root, _Text, _Variable, _Each, _If, _Else, _Call
from error import TemplateError, TemplateSyntaxError
from tokenizer import tokenize, VAR_FRAGMENT, BLOCK_FRAGMENT_START, BLOCK_FRAGMENT_END, TEXT_FRAGMENT


class Compiler(object):

    def __init__(self, template_string):
        self.template_string = template_string

    def compile(self):
        root = _Root()
        scope_stack = [root]
        for fragment in tokenize(self.template_string):
            if not scope_stack:
                raise TemplateError('nesting issues')
            parent_scope = scope_stack[-1]
            if fragment.type == BLOCK_FRAGMENT_END:
                parent_scope.exit_scope()
                scope_stack.pop()
                continue
            new_node = self.create_node(fragment)
            if new_node:
                parent_scope.children.append(new_node)
                if new_node.creates_scope:
                    scope_stack.append(new_node)
                    new_node.enter_scope()
        return root

    def create_node(self, fragment):
        node_class = None
        if fragment.type == TEXT_FRAGMENT:
            node_class = _Text
        elif fragment.type == VAR_FRAGMENT:
            node_class = _Variable
        elif fragment.type == BLOCK_FRAGMENT_START:
            cmd = fragment.clean_text.split()[0]
            if cmd == 'each':
                node_class = _Each
            elif cmd == 'if':
                node_class = _If
            elif cmd == 'else':
                node_class = _Else
            elif cmd == 'call':
                node_class = _Call
        if node_class is None:
            raise TemplateSyntaxError(fragment)
        return node_class(fragment.clean_text)


class Template(object):

    def __init__(self, contents):
        self.contents = contents
        self.root = Compiler(contents).compile()

    def render(self, **kwargs):
        return self.root.render(kwargs)


if __name__ == '__main__':
    template = Template("{{ a }}")
    print template.render(a=1)
