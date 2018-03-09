r"""
This module handles mintmod ``\ifttm`` commands.

The command is used to insert different content depending on the output format
(either HTML or PDF).

.. code-block:: latex

    \ifttm
        This only shows in HTML output.
    \else
        This shows in PDF output.
    \fi

.. warning::

    At the moment only HTML output is considered!
    (See `#15
    <https://gitlab.tu-berlin.de/innodoc/innoconv/issues/15#note_336060>`_)

"""
