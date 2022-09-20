hOLper
======

hOLper is an orienteering competition management software with a client-server
based architecture.

The minimal python version required is 3.9.

More detailed documentation is published on `<https://bodograumann.github.io/holper/>`_.

Toolkit
-------

- git (source code versioning)
- `poetry <https://www.python-poetry.org>`_ (dependencies)
- `sphinx <https://www.sphinx-doc.org>`_ (documentation)

Development
-----------

Make sure you have poetry installed. Then install the project dependencies::

    poetry install
    poetry shell

Run tests with ``pytest`` and the linter with ``pylint holper tests``.

The code can be auto-formatted with ``black holper tests``.

To generate documentation, use the following commands::

    python generate_class_diagram.py > docs/class_diagram.mmd
    cd docs
    make html

After that you can open the docs in `<docs/_build/html/index.html>`_.
