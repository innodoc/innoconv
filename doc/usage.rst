.. _usage:

How to use ``innoconv``
=======================

Run the converter in your content directory.

.. code-block:: console

  $ innoconv .

This will trigger the conversion for this content folder.

Command line arguments
----------------------

.. argparse::
   :module: innoconv.__main__
   :func: get_arg_parser
   :prog: innoconv
   :nodescription:
   :noepilog:
