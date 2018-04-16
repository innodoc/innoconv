Converting legacy mintmod content
=================================

Steps needed to adjust content sources to be used with innoConv.

All content needs to be UTF-8 encoded.

Remove ``\ifttm…\else…\fi`` commands
------------------------------------

``mintmod_ifttm`` gets rid of all ``\ifttm`` commands.

Usage:

.. code:: shell

    $ mintmod_ifttm < file_in.tex > file_out.tex

Automate on many files:

.. code:: shell

    $ find . -name '*.tex' | xargs -I % sh -c 'mintmod_ifttm < % > %_changed && mv %_changed %'

The script will only cares about ``\ifttm…\else…\fi`` with an ``\else``
command. There may be occurences of ``\ifttm…\fi`` (without ``\else``!).
Remove them manually.

Replace strings
---------------

Special characters
~~~~~~~~~~~~~~~~~~

-  ``\"a`` → ``ä``
-  ``\"o`` → ``ö``
-  ``\"u`` → ``ü``
-  ``\"A`` → ``Ä``
-  ``\"O`` → ``Ö``
-  ``\"U`` → ``Ü``

.. raw:: html

   <!-- -->

-  ``\"s`` → ``ß``
-  ``\"s`` → ``ß``
-  ``{\ss}`` → ``ß``
-  ``\ss `` → ``ß``
-  ``\ss\`` → ``ß``
-  ``\ss{}`` → ``ß``
-  ``\ss`` → ``ß``

.. raw:: html

   <!-- -->

-  ``"a`` → ``ä``
-  ``"o`` → ``ö``
-  ``"u`` → ``ü``
-  ``"A`` → ``Ä``
-  ``"O`` → ``Ö``
-  ``"U`` → ``Ü``

.. raw:: html

   <!-- -->

-  ``"``` → ``„``
-  `````` → ``„``
-  ``''`` → ``“``
-  ``"'`` → ``“``

Automate:

.. code:: shell

    find . -type f -name '*.tex' -or -name '*.rtex' | xargs sed -i 's/\\"a/ä/g'

Unwanted LaTeX
~~~~~~~~~~~~~~~~~~

-  ``\-`` → ```` (remove all occurences of hyphenation)
- remove all ``\pagebreak`` commands

``\IncludeModule``
~~~~~~~~~~~~~~~~~~

``\IncludeModule{VBKM01}{vbkm01.tex}`` becomes
``\input{VBKM01/vbkm01.tex}``.



Clean up code
~~~~~~~~~~~~~

Remove unused files.
