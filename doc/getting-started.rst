Getting started
===============

Prerequisites
-------------

innoConv is mainly used on Linux machines. It might work on Mac OS and
Windows/Cygwin/WSL. You are invited to share your experiences.

Dependencies
------------

The only dependencies you have to provide yourself is Pandoc and the Python
interpreter.

Python 3
~~~~~~~~

innoConv is developed using Python 3.9.

The software is tested against all maintained Python versions (**Python
3.6-3.9** at the time of writing).

Python should be available on the majority of Linux machines nowadays. Usually
it's installed using a package manager.

Pandoc
~~~~~~

You need to make sure to have a recent version of the :program:`pandoc` binary
available in :envvar:`$PATH` (version 2.9.2.1 at the time of writing). There are
`several ways how to install Pandoc <https://pandoc.org/installing.html>`_.

Installation
------------

Using pip
~~~~~~~~~

The easiest way to install innoConv is to use :program:`pip`.

Given you have a regular Python setup with :program:`pip` available the
following installs innoConv in your user directory (usually :file:`~/.local`
under Linux).

.. code-block:: console

  $ pip install --user innoconv

For the :program:`innoconv` command to work, make sure you have
:file:`~/.local/bin` in your :envvar:`$PATH`.

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

Install innoConv in your virtual environment using :program:`pip`.

.. code-block:: console

  $ pip install innoconv

If everything went fine you should now have access to the :program:`innoconv`
command.

The next time you login to your shell make sure to activate your virtual
environment before using :program:`innoconv`.
