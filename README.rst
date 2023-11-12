hOLper
======

hOLper is an orienteering competition management software with a client-server
based architecture.

The minimal python version required is 3.10.

More detailed documentation is published on `<https://bodograumann.github.io/holper/>`_.

Toolkit
-------

- git (source code versioning)
- `poetry <https://www.python-poetry.org>`_ (dependencies)
- `sphinx <https://www.sphinx-doc.org>`_ (documentation)

Development
-----------

Frontend
~~~~~~~~

The Vue 3 frontend can be found in the `app` folder.
You need to have node.js and npm installed.

Install dependencies::

    npm install

Compile and Hot-Reload for Development::

    npm run dev

Type-Check, Compile and Minify for Production::

    npm run build

Run Unit Tests with `Vitest <https://vitest.dev/>`_::

    npm run test:unit

Run typechecker on .ts and .vue files::

    npm run typecheck

Lint with `ESLint <https://eslint.org/>`_::

    npm run lint

Start `Storybook <https://storybook.js.org>`_::

    npm run storybook

Build a static version of the storybook::

    npm run build-storybook

Backend
~~~~~~~

Make sure you have poetry installed. Then install the project dependencies::

    poetry install
    poetry shell

Run tests with ``pytest`` and the linter with ``ruff .``.

The code can be auto-formatted with ``black holper tests``.

To generate documentation, use the following commands::

    ./generate_class_diagram.py
    cd docs
    make html

After that you can open the docs in `<docs/_build/html/index.html>`_.
