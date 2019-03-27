.. _usage:

How to use innoConv
===================

The principle way of using innoConv is using its command-line interface (CLI)
:program:`innoconv`. Another option is to use innoConv in a
:ref:`programmatic way <innoconv-as-a-library>` as a Python library.

Run the converter on your content directory.

.. code-block:: console

  $ innoconv /path/to/my/content

This will trigger the conversion and store the result in a folder
:file:`innoconv_output`. According to Unix philosophy you will not see any
messages if the conversion was successful. Though you might pass the
``--verbose`` flag to change this behaviour.

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
