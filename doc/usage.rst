.. _usage:

How to use innoConv
===================

The principle way of using innoConv is the :abbr:`CLI (Command-line interface)`
:program:`innoconv`. Another option is to use innoConv in a
:ref:`programmatic way <innoconv-as-a-library>` as Python library.

Run the converter on your content directory.

.. code-block:: console

  $ innoconv /path/to/my/content

This will trigger a conversion and store the result in a folder
:file:`innoconv_output`. A return code other than ``0`` indicates an
unsuccessful run.

.. note::

  According to Unix convention you will not see any messages if the
  conversion was successful. Though you might pass the
  :option:`--verbose <innoconv --verbose>` flag to change this behavior.

.. _command-line-arguments:

Command line arguments
----------------------

.. click:: innoconv.cli:cli
   :prog: innoconv

.. _innoconv-as-a-library:

Using innoConv as a library
---------------------------

Using innoConv within a Python program involves creating a
:class:`Manifest <innoconv.manifest.Manifest>` object and using it with a
:class:`InnoconvRunner <innoconv.runner.InnoconvRunner>`.

.. code-block:: python

  >>> manifest = Manifest(manifest_data)
  >>> runner = InnoconvRunner(source_dir, output_dir, manifest, extensions)
  >>> runner.run()

Have a look at the source of :mod:`innoconv.cli` for a more detailed example.
