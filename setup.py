from setuptools import setup, find_packages

setup(
        name='hOLper',
        version='0.0.1',
        packages=find_packages(exclude=['tests']),
        include_package_data=True,
        use_scm_version=True,

        python_requires='>=3.9',
        install_requires=[
            'PyYAML',
            'iso8601',
            'lxml',
            'more-itertools',
            'ortools',
            'python-iconv >= 1.1',
            'sqlalchemy >= 1.4',
            'typer',
            'xdg',
            'pystache',
        ],

        extras_require={
            'postgres': 'psycopg'
        },

        setup_requires=[
            'setuptools_scm'
        ],

        test_suite='tests',

        entry_points = {
            'console_scripts': [
                'holper = holper.cli:app'
            ],
        },

        description='orienteering competition management',
        url='https://github.com/bodograumann/holper',
        author='Bodo Graumann',
        author_email='mail@bodograumann.de',
        license='GPLv3',
        long_description='hOLper is a competition management software for the orienteering sport'
)
