pyMUSHRA
========

Description
-----------

pyMUSHRA is a python web application which hosts [webMUSHRA](https://github.com/audiolabs/webMUSHRA) experiments
and collects the data with python.

Installation
------------

This tool assumes to be run in a directory with the following structure:

    |- webmushra/  # The webmushra sources
    `- db/         # The TinyDB directory


You may create this structure using

    mkdir db
    git clone https://github.com/audiolabs/webMUSHRA.git webmushra
    git clone https://github.com/nils-werner/pymushra.git pymushra

    pip install -e pymushra
    pymushra server

You may also override any of the paths, i.e.

    pymushra -d somewhere/webmushra.json -w somewhere_else/webmushra/ server

Please also inspect the options using `pymushra -h`.


Debugging
---------

You may use the additional tools

    pymushra db

to load and inspect the TinyDB connection and

    pymushra df [collection]

to import and expose a DataFrame from TinyDB to experiment with.
