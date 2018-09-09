from setuptools import setup, find_packages

setup(
        name='hOLper',
        version='0.0.1',
        packages=find_packages(exclude=['tests']),
        include_package_data=True,
        use_scm_version=True,

        python_requires='>=3.4',
        install_requires=[
            'lxml',
            'PyYAML',
            'Flask',
            'Flask-GraphQL',
            'sqlalchemy >= 1.1',
            'iso8601',
            'graphene_sqlalchemy'
        ],

        extras_require={
            'postgres': 'psycopg'
        },

        setup_requires=[
            'setuptools_scm'
        ],

        test_suite='tests',

        description='orienteering competition management',
        url='https://grmnn.de/hOLper',
        author='Bodo Graumann',
        author_email='mail@bodograumann.de',
        license='GPLv3',
        long_description='hOLper is a competition management software for the orienteering sport'
)
