hOLper
======

hOLper is an orienteering competition management software with a client-server
based architecture.

Runtime Dependencies
--------------------

- ≥ python 3.4
- lxml
- PyYAML
- iso8601
- Flask
- Flask-GraphQL
- ≥ sqlalchemy 1.1
- graphene_sqlalchemy
- sqlite 3

Optional
~~~~~~~~

- postgresql server
- psycopg, for postgresql support


Toolkit
-------

- git, for version management
- sphinx, for documentation generation
    see `<http://www.sphinx-doc.org>`_
- sqlalchemy-migrate
- setuptools

Development
-----------

Setup an virtual enviroment with::

    python -m venv env
    source env/bin/activate

Run tests with ``pytest tests/test.py`` and the linter with ``python -m pylint holper tests``.
