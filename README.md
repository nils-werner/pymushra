pyMUSHRA
========

Description
-----------

pyMUSHRA is a python web application which hosts [webMUSHRA](https://github.com/audiolabs/webMUSHRA) experiments
and collects the data with python.

Quick Start
-----------

You can quickly spin up a pyMUSHRA server [using `uvx`](https://docs.astral.sh/uv/guides/tools/) or [`pipx`](https://github.com/pypa/pipx):

```sh
uvx pymushra -w <path/to/webmushra-sourcedir> server
```

or

```sh
pipx run pymushra -w <path/to/webmushra-sourcedir> server
```

Installation
------------

You can also install pyMUSHRA in a project using

```sh
uv add pymushra
uv run pymushra server
```

or

```sh
pip install pymushra
pymushra server
```

Then open <http://localhost:5000/admin/>

Debugging
---------

You may use the additional tools

```sh
uvx pymushra db
```

to load and inspect the TinyDB connection and

```sh
uvx pymushra df [collection]
```

to inspect the Pandas DataFrame export the TinyDB collection.

Server Installation
-------------------

For a long-running pyMUSHRA installation, please do not use the builtin server but instead use a proper
HTTP server, like Apache or Nginx. See [DEPLOYMENT.md](DEPLOYMENT.md) for installation instructions.
