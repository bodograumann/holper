hOLper
======

hOLper is an orienteering competition management software with a client-server
based architecture.

Dependencies are defined in `setup.py`.

Toolkit
-------

- git, for version management
- sphinx, for documentation generation
    see `<http://www.sphinx-doc.org>`_
- setuptools

Development
-----------

Setup an virtual enviroment with::

    python -m venv env
    source env/bin/activate
    pip install -r requirements.txt

Run tests with ``pytest tests/test.py`` and the linter with ``pylint holper tests``.

The code can be auto-formatted with ``black -S -l 120 holper tests``.

To generate documentation, use the following commands:

    python generate_class_diagram.py > docs/class_diagram.mmd
    cd docs
    make html

After that you can open the docs in `<docs/_build/html/index.html`.
