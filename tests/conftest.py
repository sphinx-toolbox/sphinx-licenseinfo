pytest_plugins = (
		"pytest_regressions",
		"coincidence",
		"sphinx_toolbox.testing",
		"sphinx.testing.fixtures",
		)


def pytest_sessionfinish(session, exitstatus):
	from sphinx_toolbox.utils import GITHUB_COM
	GITHUB_COM.session.close()
