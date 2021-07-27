# stdlib
from typing import Iterator

# 3rd party
import pychoosealicense
import pytest as pytest
from apeye.requests_url import RequestsURL
from importlib_resources import files
from importlib_resources.abc import Traversable


def iter_licenses() -> Iterator[pychoosealicense.License]:
	traversable: Traversable = files("pychoosealicense._licenses")
	for license_file in traversable.iterdir():
		if license_file.name.endswith(".txt"):
			yield pychoosealicense.get_license(license_file.name[:-4])


@pytest.mark.parametrize("lic", (pytest.param(l, id=l.spdx_id) for l in iter_licenses()))
def test_links(lic: pychoosealicense.License):
	"""
	Check that each license can be correctly linked to choosealicense.com
	"""

	refuri = f"https://choosealicense.com/licenses/{lic.spdx_id.lower()}/"
	assert RequestsURL(refuri).head(timeout=60)
