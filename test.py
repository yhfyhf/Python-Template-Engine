#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: yhf
# @Date:   2015-04-21 10:56:18
# @Last Modified by:   yhf
# @Last Modified time: 2015-04-21 17:00:54


import unittest
from render import Template


class TestVar(unittest.TestCase):

    def test_var(self):
        template = "<div>{{ x }}</div>"
        rendered_html = Template(template).render(x=5)
        expected_html = "<div>5</div>"
        self.assertEquals(rendered_html, expected_html)

    def test_two_vars(self):
        template = "<ul><li>{{ x }}</li><li>{{ y }}</li></ul>"
        rendered_html = Template(template).render(x=1, y=2)
        expected_html = "<ul><li>1</li><li>2</li></ul>"
        self.assertEquals(rendered_html, expected_html)

    def test_var_dict(self):
        template = '<div>{{ x }}</div>'
        rendered_html = Template(template).render(x={"a": 1})
        expected_html = "<div>{'a': 1}</div>"
        self.assertEquals(rendered_html, expected_html)


class TestEach(unittest.TestCase):

    def test_each(self):
        template = "<ul>{% each nums %}<li>{{ iter }}</li>{% end %}</ul>"
        rendered_html = Template(template).render(nums=[1, 2, 3])
        expected_html = "<ul><li>1</li><li>2</li><li>3</li></ul>"
        self.assertEquals(rendered_html, expected_html)

    def test_each_list(self):
        template = "<ul>{% each [1, 2, 3] %}<li>{{ iter }}</li>{% end %}</ul>"
        rendered_html = Template(template).render()
        expected_html = "<ul><li>1</li><li>2</li><li>3</li></ul>"
        self.assertEquals(rendered_html, expected_html)

    def test_each_tuple(self):
        template = "<ul>{% each (1, 2, 3) %}<li>{{ iter }}</li>{% end %}</ul>"
        rendered_html = Template(template).render()
        expected_html = "<ul><li>1</li><li>2</li><li>3</li></ul>"
        self.assertEquals(rendered_html, expected_html)

    def test_each_dict(self):
        template = '{% each people %}<li>{{ iter.name }} is {{ iter.age }}</li>{% end %}'
        people = [{'name': 'jack', 'age': 5}, {'name': 'rose', 'age': 6}]
        rendered_html = Template(template).render(people=people)
        expected_html = '<li>jack is 5</li><li>rose is 6</li>'
        self.assertEquals(rendered_html, expected_html)

    def test_each_nested_list(self):
        template = "{% each nums %}<ul>{% each iter %}<li>{{ iter }}</li>{% end %}</ul>{% end %}"
        nums = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        rendered_html = Template(template).render(nums=nums)
        expected_html = "<ul><li>1</li><li>2</li><li>3</li></ul><ul><li>4</li><li>5</li><li>6</li></ul><ul><li>7</li><li>8</li><li>9</li></ul>"
        self.assertEquals(rendered_html, expected_html)

    def test_nested_each_if(self):
        template = "<ul>{% each nums %}{% if iter > 1 %}<li>{{ iter }}</li>{% end %}{% end %}</ul>"
        rendered_html = Template(template).render(nums=[1, 2, 3])
        expected_html = "<ul><li>2</li><li>3</li></ul>"
        self.assertEquals(rendered_html, expected_html)


class TestIf(unittest.TestCase):

    def test_if_true(self):
        template = "{% if num > 3 %}num > 3{% end %}"
        rendered_html = Template(template).render(num=5)
        expected_html = "num > 3"
        self.assertEquals(rendered_html, expected_html)

    def test_if_false(self):
        template = "{% if num > 5 %}num > 5{% end %}"
        rendered_html = Template(template).render(num=3)
        expected_html = ""
        self.assertEquals(rendered_html, expected_html)

    def test_nested_if_else(self):
        template = "{% if num > 3 %}num > 3 and {% if num > 10 %}num > 10{% else %}num <= 10{% end %}{% else %}num <= 3{% end %}"
        rendered_html = Template(template).render(num=5)
        expected_html = "num > 3 and num <= 10"
        self.assertEquals(rendered_html, expected_html)

    def test_if_boolean(self):
        template = "{% if flag %}Not None{% end %}"
        rendered_html = Template(template).render(flag="hello")
        expected_html = "Not None"
        self.assertEquals(rendered_html, expected_html)


class TestCall(unittest.TestCase):

    @staticmethod
    def add(x=1, y=2):
        return x + y

    def test_call(self):
        template = "{% call len 'abc' %}"
        rendered_html = Template(template).render(len=len)
        expected_html = "3"
        self.assertEquals(rendered_html, expected_html)

    def test_call_params(self):
        template = "{% call add 2 3 %}"
        rendered_html = Template(template).render(add=TestCall.add)
        expected_html = "5"
        self.assertEquals(rendered_html, expected_html)

    def test_call_kwargs0(self):
        template = "{% call add %}"
        rendered_html = Template(template).render(add=TestCall.add)
        expected_html = "3"
        self.assertEquals(rendered_html, expected_html)

    def test_call_kwargs1(self):
        template = "{% call add y=3 %}"
        rendered_html = Template(template).render(add=TestCall.add)
        expected_html = "4"
        self.assertEquals(rendered_html, expected_html)

    def test_call_kwargs2(self):
        template = "{% call add x=2 y=3 %}"
        rendered_html = Template(template).render(add=TestCall.add)
        expected_html = "5"
        self.assertEquals(rendered_html, expected_html)


if __name__ == '__main__':
    unittest.main()
