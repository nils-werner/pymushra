pyMUSHRA
========

Description
-----------

pyMUSHRA is a python web application which hosts [webMUSHRA](https://github.com/audiolabs/webMUSHRA) experiments
and collects the data with python.

Quick Start
-----------

This tool assumes to be run in a directory with the following structure:

    |- webmushra/  # The webmushra sources
    `- db/         # The TinyDB directory

You can quickly create this and install pymushra using

    cd /path/to/venv
    python3 -m venv .
    source bin/activate

    mkdir db
    git clone https://github.com/audiolabs/webMUSHRA.git webmushra
    git clone https://github.com/nils-werner/pymushra.git pymushra

    pip install -e pymushra
    pymushra server

Then open <http://localhost:5000/admin/>

Debugging
---------

You may use the additional tools

    pymushra db

to load and inspect the TinyDB connection and

    pymushra df [collection]

to inspect the Pandas DataFrame export the TinyDB collection.

Server Installation
-------------------

For a long-running pyMUSHRA installation, please do not use the builtin server but instead use a proper
HTTP server, like Apache or Nginx. See [DEPLOYMENT.md](DEPLOYMENT.md) for installation instructions.
