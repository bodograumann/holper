hOLper
======

hOLper is an orienteering competition management software with a client-server
based architecture.

The minimal python version required is 3.9.

Toolkit
-------

- git (source code versioning)
- `poetry <https://www.python-poetry.org>`_ (dependencies)
- `sphinx <http://www.sphinx-doc.org>`_ (documentation)

Development
-----------

Make sure you have poetry installed. Then install the project dependencies::

    poetry install
    poetry shell

Run tests with ``pytest tests/test.py`` and the linter with ``pylint holper tests``.

The code can be auto-formatted with ``black -S -l 120 holper tests``.

To generate documentation, use the following commands::

    python generate_class_diagram.py > docs/class_diagram.mmd
    cd docs
    make html

After that you can open the docs in `<docs/_build/html/index.html`.
