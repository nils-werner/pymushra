#!/usr/bin/env python

import setuptools

if __name__ == "__main__":
    setuptools.setup(
        name='pymushra',
        version='0.3',

        description='webMUSHRA server in Python',
        author='Nils Werner, Fabian-Robert Stöter',
        author_email='nils.werner@audiolabs-erlangen.de',

        license='MIT',
        packages=setuptools.find_packages(),

        install_requires=[
            'numpy',
            'matplotlib>=2.0.0',
            'scipy',
            'ipython',
            'flask>=2.2.5',
            'pandas>=0.24.0',
            'seaborn',
            'statsmodels',
            'patsy',
            'tinydb>=3.0.0',
            'tinyrecord',
            'pytest',
            'click',
        ],

        entry_points={'console_scripts': [
            'pymushra=pymushra.cli:cli'
        ]},

        zip_safe=True,
        include_package_data=True,
    )
