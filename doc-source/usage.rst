===========
Usage
===========

.. extensions:: sphinx_licenseinfo


Directives
--------------


.. rst:directive:: license

	Shows the text of a license.

	Exactly one of the following options must be provided:

	.. rst:directive:option:: py
		:type: string

		Obtain the license text from the ``LICENSE`` file
		of the given Python project's ``.dist-info`` metadata directory.

	.. rst:directive:option:: file
		:type: flag

		Obtain the license text from the given file, relative to the Sphinx source directory
		(i.e. the directory containing ``conf.py``).



.. rst:directive:: .. license-info:: license

	Shows information about a license.

	The license information is obtained from `choosealicense.com`_.

	``license`` is the SPDX_ identifier for the license.


Roles
--------


.. rst:role:: choosealicense

	Creates a cross-reference to a license on `choosealicense.com`_.

	The licenses are referred to by their SPDX_ identifier (e.g. ``mit``), matched case insensitively.
	The title of the license (e.g. ``MIT License``) is inserted into the document
	as a hyperlink to the license information page on `choosealicense.com`_.

	A custom title can be added to the link by writing :samp:`:choosealicense:\`title <spdx_id>\``.

	This role also generates an appropriate index entry.


.. _choosealicense.com: https://choosealicense.com/
.. _SPDX: https://spdx.org/licenses/
