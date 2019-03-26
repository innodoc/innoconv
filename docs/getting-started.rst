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

Python 3.6
~~~~~~~~~~

While other versions of Python might work, innoConv has been tested and
developed with **Python 3.6**. It should be available on your Linux machine.
Usually it's installed using your distribution package management.

Pandoc
~~~~~~

You need to make sure to have a recent version of the ``pandoc`` binary
available in ``PATH`` (**Pandoc 2.7** at the time of writing). There are
`several ways on installing Pandoc <https://pandoc.org/installing.html>`_.

Installation
------------

Using pip
~~~~~~~~~

The easiest way to install innoConv is to use pip.

Given you have a regular Python setup with pip available the following installs
innoConv in your user directory (usually ``~/.local`` under Linux).

.. code-block:: console

  $ pip install --user innoconv

For the ``innoconv`` command to work, make sure you have ``~/.local/bin`` in
your ``$PATH``.

For a system-wide installation you can omit the ``--user`` argument.

.. code-block:: console

  $ pip install innoconv

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

The next time you login to your shell make sure to activate your virtual
environment before using ``innoconv``.
