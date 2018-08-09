Getting started
===============

Prerequisites
-------------

innoConv is mainly used on Linux machines. It might work on Mac OS and
Windows/Cygwin/WSL. You are invited to share experiences in doing so.

Dependencies
------------

The only dependencies you have to provide yourself is Pandoc and the Python
interpreter.

Python interpreter
~~~~~~~~~~~~~~~~~~

While other versions of Python might work fine, innoConv was tested with
**Python 3.6**. Make sure you have it installed.

Pandoc
~~~~~~

You need to make sure to have a recent version of the pandoc binary available
in ``PATH`` (**Pandoc 2.2.1** at the time of writing). There are `several ways
on installing Pandoc <https://pandoc.org/installing.html>`_.

Installation
------------

Using pip
~~~~~~~~~

TODO

In a virtual environment
~~~~~~~~~~~~~~~~~~~~~~~~

It's possible to install innoConv into a virtual environment. Setup and
activate a virtual environment in a location of your choice.

.. code-block:: console

  $ python3 -m venv /path/to/venv
  $ source /path/to/venv/bin/activate

Install innoConv in your virtual environment using pip.

.. code-block:: console

  $ pip install innoconv

If everything went fine you should now have access to the ``innoconv`` command.

.. code-block:: console

  $ innoconv -h
  usage: innoconv [-h] [-l LANGUAGES] [-o OUTPUT_DIR_BASE] [-d] source_dir

    Convert interactive educational content.

  positional arguments:
    source_dir            content directory or file

  optional arguments:
    -h, --help            show this help message and exit
    -l LANGUAGES, --languages LANGUAGES
                          languages to convert (default: "de,en")
    -o OUTPUT_DIR_BASE, --output-dir-base OUTPUT_DIR_BASE
                          output base directory (default: "/store/cosmetix/datastore/dietrich/dev/innoconv/innoconv_output")
    -d, --debug           debug mode

  Copyright (C) 2018 innoCampus, TU Berlin
  Authors: Mirko Dietrich
  Web: https://gitlab.tu-berlin.de/innodoc/innoconv

  This is free software; see the source for copying conditions. There is no
  warranty, not even for merchantability or fitness for a particular purpose.

The next time you login to your shell make sure to activate your virtual
environment before using ``innoconv``.
