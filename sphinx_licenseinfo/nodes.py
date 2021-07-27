#!/usr/bin/env python3
#
#  nodes.py
"""
Custom docutils nodes.
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
from docutils import nodes
from pychoosealicense import License

__all__ = ["custom_transition", "flushright_text", "license_info"]


class custom_transition(nodes.Structural, nodes.Element):
	"""
	Docutils node for a transition line.

	.. seealso:: :class:`docutils.nodes.transition`
	"""


class flushright_text(nodes.paragraph):
	"""
	Docutils node for a paragraph that will be displayed as flushleft with the LaTeX builder.
	"""


class license_info(nodes.paragraph):
	r"""
	Docutils node representing information about a license.

	:param rawsource:
	:param text:
	:param \*children:
	:param license: The license object itself.
	:type license: :class:`~pychoosealicense.License`
	:param \*\*attributes:
	"""

	license: License  # noqa: A003  # pylint: disable=redefined-builtin

	def __init__(self, rawsource: str = '', text: str = '', *children: nodes.Node, **attributes):
		if text != '':  # pragma: no cover
			textnode = nodes.Text(text)
			nodes.Element.__init__(self, rawsource, textnode, *children, **attributes)
		else:
			nodes.Element.__init__(self, rawsource, *children, **attributes)

		if "license" in attributes:
			self.license = attributes["license"]
		else:  # pragma: no cover
			raise TypeError("license_info() missing 1 required keyword-only argument: 'license'")
