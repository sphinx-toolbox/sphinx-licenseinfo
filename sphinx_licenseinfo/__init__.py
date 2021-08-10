#!/usr/bin/env python3
#
#  __init__.py
"""
Sphinx directives for showing license information.

.. _choosealicense.com: https://choosealicense.com/
"""
#
#  Copyright © 2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  HTML styling and license-sprite.png from https://github.com/github/choosealicense.com
#  Copyright (c) 2013-2021 GitHub, Inc. and contributors
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

# stdlib
import textwrap
from typing import Any, Dict, Iterable, List, Optional, Tuple

# 3rd party
import docutils.nodes
from dist_meta.distributions import get_distribution
from docutils.parsers.rst import directives
from docutils.statemachine import StringList
from domdf_python_tools.compat import importlib_resources
from domdf_python_tools.paths import PathPlus
from pychoosealicense import description as description_utils
from pychoosealicense import get_license
from pychoosealicense.rules import Rule
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.util.docutils import ReferenceRole, SphinxDirective
from sphinx.writers.html5 import HTML5Translator
from sphinx_toolbox.utils import Purger

# this package
from sphinx_licenseinfo import nodes

__author__: str = "Dominic Davis-Foster"
__copyright__: str = "2021 Dominic Davis-Foster"
__license__: str = "MIT License"
__version__: str = "0.1.2"
__email__: str = "dominic@davis-foster.co.uk"

__all__ = [
		"ChooseALicenseRole",
		"LicenseDirective",
		"LicenseInfoDirective",
		"setup",
		]

license_node_purger = Purger("all_license_nodes")


class LicenseDirective(SphinxDirective):
	"""
	Directive for showing a license.

	The license can be taken from a Python package's metadata,
	or from a filename relative to the Sphinx source directory.
	"""

	option_spec = {
			"py": directives.unchanged_required,  # from python .dist-info
			"file": directives.unchanged_required,  # from the file, relative to Sphinx srcdir
			}

	def run(self) -> List[docutils.nodes.Node]:
		"""
		Process the content of the directive.
		"""

		output = []

		if len(self.options) != 1:
			return self.problematic(f"'.. license::' requires exactly one option, got {len(self.options)}")

		elif "py" in self.options:
			distro = get_distribution(self.options["py"])

			license_files = sorted(f.name for f in distro.path.glob("LICEN[CS]E*"))

			if not license_files:
				return self.problematic(
						f"No 'LICENSE' file (or similar) found "
						f"for distribution {distro.name!r} version {distro.version}"
						)

			if len(license_files) > 1:
				self.state.reporter.warning(
						f"Found more than one file matching the pattern 'LICEN[CS]E*' "
						f"for distribution {distro.name!r} version {distro.version}\n"
						f"Using the first one.",
						line=self.lineno,
						)

			license_text = distro.read_file(next(iter(license_files)))

		elif "file" in self.options:
			src_dir = PathPlus(self.env.srcdir)
			license_file = src_dir / self.options["file"]
			license_text = license_file.read_text()

		else:  # pragma: no cover
			# Should never occur
			output.extend(self.problematic(f"Unknown option to '.. license::': {next(iter(self.options))}"))
			return output

		content = [".. code-block:: none", '']
		content.extend(textwrap.indent(license_text, "    ").split('\n'))

		license_node = docutils.nodes.paragraph(rawsource='\n'.join(content))
		self.state.nested_parse(StringList(content), self.content_offset, license_node)
		output.append(license_node)
		return output

	def problematic(self, message: str) -> List[docutils.nodes.problematic]:
		"""
		Reports an error while processing the directive.

		:param message:
		"""

		msg = self.state.reporter.warning(message, line=self.lineno)
		prob_node = docutils.nodes.problematic(self.block_text, self.block_text, msg)
		return [prob_node]


class LicenseInfoDirective(SphinxDirective):
	"""
	Directive for showing information about a license.

	The license information is obtained from `choosealicense.com`_.
	"""  # noqa: RST306

	required_arguments = 1  # the license's SPDX identifier

	def run(self) -> List[docutils.nodes.Node]:
		"""
		Process the content of the directive.
		"""

		the_license = get_license(self.arguments[0])

		license_node = nodes.license_info(license=the_license)
		license_node += nodes.custom_transition()

		description = description_utils.as_rst(the_license.description)
		description_node = docutils.nodes.paragraph('')
		license_node += description_node
		self.state.nested_parse(StringList([description]), self.content_offset, description_node)

		license_node.extend(self.add_rules_list("Permissions", the_license.permissions))
		license_node.extend(self.add_rules_list("Conditions", the_license.conditions))
		license_node.extend(self.add_rules_list("Limitations", the_license.limitations))

		see_more_node = nodes.flushright_text('')
		license_node += see_more_node
		self.state.nested_parse(
				StringList([
						f":choosealicense:`See more information on choosealicense.com ➩ <{the_license.spdx_id.lower()}>`"
						]),
				self.content_offset,
				see_more_node
				)

		license_node += nodes.custom_transition()

		return [license_node]

	def add_rules_list(self, category: str, rules: Iterable[Rule]):
		"""
		Add a heading for a rule category, followed by a bullet-point list of the rules in that category.

		:param category: The category label.
		:param rules: The rules.
		"""

		content = [
				f"**{category}**",
				'',
				*(f"* {rule.label} -- {rule.description}" for rule in rules),
				'',
				]

		rules_node = docutils.nodes.paragraph('')
		self.state.nested_parse(StringList(content), self.content_offset, rules_node)

		return [docutils.nodes.raw('', r"\vspace{10px}", format="latex"), rules_node]


class ChooseALicenseRole(ReferenceRole):
	"""
	Sphinx role for referencing a license on `choosealicense.com`_.
	"""  # noqa: RST306

	title: Optional[str]
	target: Optional[str]
	has_explicit_title: Optional[bool]

	def run(self) -> Tuple[List[docutils.nodes.Node], List[docutils.nodes.system_message]]:
		"""
		Process the role.
		"""

		assert self.title is not None
		assert self.target is not None
		assert self.inliner is not None

		the_license = get_license(self.target)

		self.target = the_license.spdx_id

		if not self.has_explicit_title:
			self.title = the_license.title

		target_id = f"index-{self.env.new_serialno('index')}"
		entries = [("single", the_license.title, target_id, '', None)]

		index = addnodes.index(entries=entries)
		target = docutils.nodes.target('', '', ids=[target_id])
		self.inliner.document.note_explicit_target(target)  # type: ignore

		refuri = f"https://choosealicense.com/licenses/{the_license.spdx_id.lower()}/"
		reference = docutils.nodes.reference('', '', internal=False, refuri=refuri, classes=["pep"])
		reference += docutils.nodes.inline(self.title, self.title)

		return [index, target, reference], []


def copy_asset_files(app: Sphinx, exception: Optional[Exception] = None):
	"""
	Copy additional stylesheets into the HTML build directory.

	:param app: The Sphinx application.
	:param exception: Any exception which occurred and caused Sphinx to abort.
	"""

	if exception:  # pragma: no cover
		return

	if app.builder.format.lower() != "html":
		return

	static_dir = PathPlus(app.outdir) / "_static"
	static_dir.maybe_make(parents=True)

	css_dir = static_dir / "css"
	css_dir.maybe_make()

	with importlib_resources.open_text("sphinx_licenseinfo", "license_info.css") as fp:
		(css_dir / "license_info.css").write_text(fp.read())

	img_dir = static_dir / "img"
	img_dir.maybe_make()

	for filename in ("license-sprite@2x.png", "license-sprite.png"):
		with importlib_resources.open_binary("sphinx_licenseinfo", filename) as fp2:
			(css_dir / filename).write_bytes(fp2.read())


def _configure(app: Sphinx):
	kwargs = {}
	translation_handlers = app.registry.translation_handlers
	translator = app.registry.translators.get(
			app.builder.name,
			app.builder.default_translator_class,
			)

	if translator:

		if app.builder.name in translation_handlers:
			builder_name_or_format = app.builder.name

		else:
			# Add the version for the format instead
			builder = app.registry.builders[app.builder.format]
			translator = app.registry.translators.get(builder.name, builder.default_translator_class)
			builder_name_or_format = app.builder.format

			if isinstance(translator, property):  # https://github.com/sphinx-doc/sphinx/issues/9496
				if translator.fget is StandaloneHTMLBuilder.default_translator_class.fget:
					translator = HTML5Translator
				else:
					return

		kwargs[builder_name_or_format] = (
				translator.visit_transition,
				getattr(translator, "depart_transition", lambda *args: None),
				)

		app.add_node(nodes.custom_transition, **kwargs)  # type: ignore


def setup(app: Sphinx) -> Dict[str, Any]:
	"""
	Setup :mod:`sphinx_licenseinfo`.

	:param app: The Sphinx application.
	"""

	# this package
	from sphinx_licenseinfo.translators import (
			depart_flushright_text,
			depart_license_info,
			visit_flushright_text,
			visit_license_info
			)

	app.setup_extension("sphinx_toolbox.formatting")

	app.add_directive("license", LicenseDirective)
	app.add_directive("license-info", LicenseInfoDirective)
	app.add_role("choosealicense", ChooseALicenseRole())

	app.connect("builder-inited", _configure)
	app.connect("env-purge-doc", license_node_purger.purge_nodes)
	app.connect("env-get-outdated", license_node_purger.get_outdated_docnames)
	app.connect("build-finished", copy_asset_files)

	app.add_css_file("css/license_info.css")

	app.add_node(nodes.flushright_text, latex=(visit_flushright_text, depart_flushright_text))
	app.add_node(nodes.license_info, html=(visit_license_info, depart_license_info))

	return {
			"version": __version__,
			"parallel_read_safe": True,
			"parallel_write_safe": True,
			}
