#!/usr/bin/env python3
#
#  translators.py
"""
Node visitors for custom nodes.
"""
#
#  Copyright © 2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#

# 3rd party
import docutils.nodes
import jinja2
import pychoosealicense.description
from domdf_python_tools.compat import importlib_resources
from sphinx.builders.latex.nodes import footnotetext
from sphinx.writers.html5 import HTML5Translator
from sphinx.writers.latex import LaTeXTranslator

# this package
from sphinx_licenseinfo import nodes

__all__ = ["visit_flushright_text", "depart_flushright_text", "visit_license_info", "depart_license_info"]


def visit_flushright_text(translator: LaTeXTranslator, node: nodes.flushright_text):
	"""
	Visit a :class:`~.flushright_text` node and generate LaTeX output.

	:param translator:
	:param node:
	"""

	translator.body.append("\\begin{flushright}\n")

	index = node.parent.index(node)
	sibling = node.parent[index - 1]

	if (
			index > 0 and isinstance(node.parent, docutils.nodes.compound)
			and not isinstance(sibling, docutils.nodes.paragraph)
			and not isinstance(sibling, docutils.nodes.compound)
			):
		# insert blank line, if the paragraph follows a non-paragraph node in a compound
		translator.body.append("\\noindent\n")  # pragma: no cover
	elif index == 1 and isinstance(node.parent, (docutils.nodes.footnote, footnotetext)):
		# don't insert blank line, if the paragraph is second child of a footnote
		# (first one is label node)
		pass  # pragma: no cover
	else:
		# Sphinx 3.5 adds \sphinxAtStartPar here, but I don't see what it gains.
		translator.body.append('\n')

	translator.body.append("$POP_TO_HERE$")


def depart_flushright_text(translator: LaTeXTranslator, node: nodes.flushright_text):
	"""
	Depart a :class:`~.flushright_text` node and generate LaTeX output.

	:param translator:
	:param node:
	"""

	node_content = []

	while True:
		item = translator.body.pop()
		if item == "$POP_TO_HERE$":
			break
		else:
			node_content.append(item.replace('➩', r"{}$\Rightarrow${}"))

	translator.body.extend(reversed(node_content))
	translator.body.append("\n\\end{flushright}\n")


def visit_license_info(translator: HTML5Translator, node: nodes.license_info):
	"""
	Visit a :class:`~.license_info` node and generate HTML output.

	:param translator:
	:param node:
	"""

	template_source = importlib_resources.read_text("sphinx_licenseinfo", "license_info.t.html")
	license_template = jinja2.Environment(  # nosec: B701
		loader=jinja2.BaseLoader(),
		undefined=jinja2.StrictUndefined,
		autoescape=jinja2.select_autoescape()
		).from_string(template_source)

	the_description = pychoosealicense.description.as_html(node.license.description)
	output = license_template.render(license=node.license, description=the_description).split('\n')

	translator.body.extend(output)
	raise docutils.nodes.SkipNode


def depart_license_info(translator: HTML5Translator, node: nodes.license_info):
	"""
	Depart a :class:`~.license_info` node and generate HTML output.

	:param translator:
	:param node:
	"""
