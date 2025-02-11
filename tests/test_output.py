# stdlib
import shutil
from typing import Iterator, cast

# 3rd party
import bs4.element  # type: ignore[import]
import docutils
import handy_archives
import pychoosealicense as pychoosealicense
import pytest
import sphinx
from bs4 import BeautifulSoup
from coincidence.params import param
from consolekit.terminal_colours import strip_ansi
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.stringlist import StringList
from importlib_resources import files
from importlib_resources.abc import Traversable
from sphinx.application import Sphinx
from sphinx.builders import Builder
from sphinx_toolbox.testing import HTMLRegressionFixture, LaTeXRegressionFixture


def iter_licenses() -> Iterator[pychoosealicense.License]:
	traversable: Traversable = files("pychoosealicense._licenses")
	for license_file in traversable.iterdir():
		if license_file.name.endswith(".txt"):
			yield pychoosealicense.get_license(license_file.name[:-4])


@pytest.fixture()
def doc_root(tmp_pathplus: PathPlus) -> None:
	doc_root = tmp_pathplus.parent / "test-sphinx-licenseinfo"
	doc_root.maybe_make()
	(doc_root / "conf.py").write_lines([
			"extensions = ['sphinx_licenseinfo']",
			"toml_spec_version = '0.5.0'",
			])

	shutil.copy2(PathPlus(__file__).parent / "index.rst", doc_root / "index.rst")

	examples_dir = doc_root / "examples"
	examples_dir.maybe_make()


_original_wheel_directory = PathPlus(__file__).parent / "wheels"


@pytest.fixture(scope="session")
def wheel_directory() -> PathPlus:
	return _original_wheel_directory


@pytest.fixture()
def fake_virtualenv(
		wheel_directory: PathPlus,
		tmp_pathplus: PathPlus,
		monkeypatch,
		) -> None:

	site_packages = (tmp_pathplus / "python3.8" / "site-packages")

	site_packages.mkdir(parents=True)

	for filename in [
			"Sphinx-3.5.4-py3-none-any.whl",
			"packaging-21.0-py3-none-any.whl",
			"CacheControl-0.12.6-py2.py3-none-any.whl",
			]:

		handy_archives.unpack_archive(str(wheel_directory / filename), site_packages)

	monkeypatch.syspath_prepend(str(site_packages))


@pytest.mark.usefixtures("doc_root")
@pytest.mark.sphinx("html", testroot="test-sphinx-licenseinfo")
def test_build_example(app: Sphinx):
	app.build()
	app.build()


def check_html_output(
		page: BeautifulSoup,
		html_regression: HTMLRegressionFixture,
		extension: str = ".html",
		) -> None:

	code: bs4.element.Tag
	for code in page.find_all("code", attrs={"class": "sig-prename descclassname"}):
		first_child = code.contents[0]
		if isinstance(first_child, bs4.element.Tag):
			code.contents = [first_child.contents[0]]

	for code in page.find_all("code", attrs={"class": "sig-name descname"}):
		first_child = code.contents[0]
		if isinstance(first_child, bs4.element.Tag):
			code.contents = [first_child.contents[0]]

	html_regression.check(page, extension=extension)


@pytest.mark.usefixtures("doc_root", "fake_virtualenv")
@pytest.mark.sphinx("html", testroot="test-sphinx-licenseinfo")
def test_html_output(
		app: Sphinx,
		html_regression: HTMLRegressionFixture,
		):

	srcdir = PathPlus(app.srcdir)

	for file in ["bsd-2-clause.rst", "gpl-3.0.rst", "lgpl-3.0.rst", "mit.rst", "pep639.rst"]:
		shutil.copy2(PathPlus(__file__).parent / "examples" / file, srcdir / "examples" / file)

	shutil.copy2(PathPlus(__file__).parent / "GIMP_COPYING", srcdir / "GIMP_COPYING")

	app.build()

	if docutils.__version_info__ >= (0, 17):
		section = "section"
		end_section = "section"
	else:
		section = 'div class="section"'
		end_section = "div"

	for lic in ["bsd-2-clause", "gpl-3.0", "lgpl-3.0", "mit"]:
		output_file = PathPlus(app.outdir) / "examples" / f"{lic}.html"
		page = BeautifulSoup(output_file.read_text(), "html5lib")
		html_regression.check(
				page,
				jinja2=True,
				jinja2_namespace={"section": section, "end_section": end_section},
				extension=f"_{lic}.html"
				)


@pytest.mark.parametrize("lic", (param(l, id=l.spdx_id) for l in iter_licenses()))
@pytest.mark.usefixtures("doc_root", "fake_virtualenv")
@pytest.mark.sphinx("html", testroot="test-sphinx-licenseinfo")
def test_html_output_licenses(
		app: Sphinx,
		html_regression: HTMLRegressionFixture,
		lic: pychoosealicense.License,
		):

	licenses_dir = PathPlus(app.srcdir) / "licenses"
	licenses_dir.maybe_make()
	(licenses_dir / "index.rst").touch()

	(licenses_dir / f"{lic.spdx_id}.rst").write_lines([
			":orphan:",
			'',
			"================================================",
			f':choosealicense:`{lic.spdx_id}`',
			"================================================",
			'',
			f'.. license-info:: {lic.spdx_id}',
			'',
			])

	app.build()

	output_file = PathPlus(app.outdir) / "licenses" / f"{lic.spdx_id}.html"
	page = BeautifulSoup(output_file.read_text(), "html5lib")

	if docutils.__version_info__ >= (0, 17):
		section = "section"
		end_section = "section"
	else:
		section = 'div class="section"'
		end_section = "div"

	html_regression.check(page, jinja2=True, jinja2_namespace={"section": section, "end_section": end_section})


@pytest.mark.usefixtures("doc_root", "fake_virtualenv")
@pytest.mark.sphinx("html", testroot="test-sphinx-licenseinfo")
def test_html_output_problematic(
		app: Sphinx,
		html_regression: HTMLRegressionFixture,
		):

	shutil.copy2(PathPlus(__file__).parent / "problematic.rst", PathPlus(app.srcdir) / "problematic.rst")
	app.build()
	capout = strip_ansi(app._warning.getvalue())  # type: ignore[attr-defined]

	expeted_warnings = [
			"problematic.rst:7: WARNING: '.. license::' requires exactly one option, got 0",
			"problematic.rst:9: WARNING: Found more than one file matching the pattern 'LICEN[CS]E*' "
			"for distribution 'packaging' version 21.0\nUsing the first one.",
			"problematic.rst:12: WARNING: No 'LICENSE' file (or similar) found for distribution 'CacheControl' version 0.12.6",
			]

	if sphinx.version_info >= (4, 4):
		# if docutils.__version_info__ >= (0, 17):
		expeted_warnings.append(
				'problematic.rst:15: ERROR: Error in "license" directive:\nno content permitted.\n\n.. license:: sphinx\n',
				)
	else:
		expeted_warnings.append(
				'problematic.rst:15: WARNING: Error in "license" directive:\nno content permitted.\n\n.. license:: sphinx\n',
				)

	for string in expeted_warnings:
		assert string in capout

	output_file = PathPlus(app.outdir) / "problematic.html"
	page = BeautifulSoup(output_file.read_text(), "html5lib")

	if docutils.__version_info__ >= (0, 17):
		section = "section"
		end_section = "section"
	else:
		section = 'div class="section"'
		end_section = "div"

	html_regression.check(page, jinja2=True, jinja2_namespace={"section": section, "end_section": end_section})


@pytest.mark.usefixtures("doc_root", "fake_virtualenv")
@pytest.mark.sphinx("latex", testroot="test-sphinx-licenseinfo")
def test_latex_output(
		app: Sphinx,
		latex_regression: LaTeXRegressionFixture,
		):

	srcdir = PathPlus(app.srcdir)

	assert cast(Builder, app.builder).name.lower() == "latex"

	for file in ["bsd-2-clause.rst", "gpl-3.0.rst", "lgpl-3.0.rst", "mit.rst", "pep639.rst"]:
		shutil.copy2(
				PathPlus(__file__).parent / "examples" / file,
				srcdir / "examples" / file,
				)

	shutil.copy2(
			PathPlus(__file__).parent / "GIMP_COPYING",
			srcdir / "GIMP_COPYING",
			)

	app.build()

	output_file = PathPlus(app.outdir) / "python.tex"

	latex_regression.check(StringList(output_file.read_lines()), jinja2=True)
