Conventions
===========

* use editorconfig
* write unit tests

To run the tests, execute `python -m unittest`.

Python
------

* Track dependencies in setup.py and README.rst

* documentation with sphinx/restructured text (`<http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html>`_, `<http://sphinx-doc.org>`_)

* require python 3.4 (e.g. for enums → sqlalchemy 1.1)

* conform to PEP8, PEP257, PEP287
* use single quotes, except for docstrings
* use doctests if useful as documentation
* use pytest

Restructured Text
-----------------

* Title characters:

  * "================"
  * "----------------"
  * "~~~~~~~~~~~~~~~~"
  * "````````````````"
  * "^^^^^^^^^^^^^^^^"
  * "****************"
  * "++++++++++++++++"
  * "::::::::::::::::"

Database
--------

* capitalization: SOME_KEYWORD, SomeTable, some_table_id, some_column
	(compare `<http://www.vertabelo.com/blog/technical-articles/naming-conventions-in-database-modeling>`_)

