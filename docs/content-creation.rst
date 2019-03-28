Content creation
================

This section deals with the creation of content files that are fed into
innoConv for processing.

As already mentioned, the main format for writing content is Markdown. The
available references for the Markdown language generally do apply for innoConv
but we will direct you specifically to
`Pandoc's Markdown <https://pandoc.org/MANUAL.html#pandocs-markdown>`_. The
reason for that is Markdown exists in different flavours  and innoConv is using
Pandoc under the hood.

.. seealso::

  The :ref:`example-course` serves as a reference to authors.

Best practices
--------------

Text editor
~~~~~~~~~~~

Content is written in plain-text. Therefore you will need a text editor to
author innoDoc content. The choices are endless. If in doubt your operating
system comes with a text editor pre-installed.

.. warning::

  Please use *UTF-8 character encoding* exclusively when writing documents for
  innoConv. Make sure your editor uses the right encoding.

Version control
~~~~~~~~~~~~~~~

Writing large amounts of text is often a joint effort with a lot of edits and
many contributors. Using a :abbr:`VCS (Version control system)` (e.g.
`git <https://git-scm.com/>`_) for personal use is highly recommended. On a
collaborative project it's indispensable.

Writing content
---------------

Your content typically resides in a dedicated directory referred to as *root
directory* from now on. There are some conventions that you need to follow.
These are explained in this section.

The manifest file
~~~~~~~~~~~~~~~~~

The root directory is home to the :file:`manifest.yml` file. It is used to
store meta information about your content, like the title, the languages and so
on.

.. code-block:: yaml
  :caption: A minimal example for a content manifest.

  title:
    en: Example course
    de: Beispielkurs
  languages: en,de

.. note::

  If your content uses only one language, you will still need to put this
  single language here.

.. _directory-and-file-structure:

Directory and file structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _sections_and_subsections:

Sections and subsections
````````````````````````

In the previous section we saw how to specify the available languages for the
content. For every language one sub-directory needs to exist in the root
directory.

Under each language directory there is a structure of folders reflecting the
part/chapter/section structure of the text.

.. note:: Every directory needs one :file:`content.md`.

The names of the directories determine the order in the actual text. They are
sorted alphanumerically. The directory name itself can be used to create
:ref:`cross-references <xrefs>` from one part in the the text to another. Also,
they might appear in more technical contexts such as
:abbr:`URLs (Uniform Resource Locator)`.

.. note::
  While technically not strictly required, for convenience it's advisable to
  limit directory names to characters, numbers, hyphen and underscore
  (``a-z``, ``0-9``, ``-`` and ``_``).

.. code-block:: text
  :caption: Example directory structure for two languages.

  root
  ├── manifest.yml
  ├── en
  |   ├── content.md
  |   ├── 01-part
  |   |   ├── content.md
  |   |   ├── 01-section
  |   |   |   └── content.md
  |   |   └── …
  |   └── …
  └── de
      ├── content.md
      ├── 01-part
      |   ├── content.md
      |   ├── 01-section
      |   |   └── content.md
      |   └── …
      └── …

.. important::

  The directory structure in each of the language folders need to match!

.. _static_files:

Static files
````````````

There can be optional directories :file:`_static` for media files.

These can exist in two different locations: Either at the root folder or inside
a language folder. Some files might have a translated version. To account for
this a localized version of the file can be put in the language's static
folder.

.. code-block:: text
  :caption: Locations for static files.

  root
  ├── _static
  |   ├── chart.svg
  |   └── image.png
  ├── en
  |   ├── _static
  |   |   └── video.mp4
  └── de
      └── _static
          └── video.mp4

*For the sake of clarity other needed files and directories are omitted in this
listing.*

.. _content_files:

Content files
~~~~~~~~~~~~~

A file :file:`content.md` needs to exist in every section folder. It has a
small section at the top of the file called
`YAML metadata block <https://pandoc.org/MANUAL.html#extension-yaml_metadata_block>`_
that contains the section title.

.. code-block:: yaml
  :caption: Example YAML metadata block.

  ---
  title: Example title for this section
  ---

After the metablock you can write your actual content.

.. note::

  A :file:`content.md` needs to exist for every language version, e.g.
  :file:`en/section01/content.md` and :file:`de/section01/content.md`.

This section will not provide an exhaustive list of formatting options. Instead
it will mainly focus on some features that are unique to innoDoc.

.. seealso::

  All possibilities are documented in the
  :ref:`example course <example-course>`.

.. _media-files:

Media files
```````````

.. todo:: Media files

.. _pgf-tikz:

PGF/Ti\ *k*\ Z
``````````````

|pgftikz|_ is used to create vector graphics and is written in TeX.

.. _pgftikz: https://sourceforge.net/projects/pgf/

.. |pgftikz| replace:: PGF/Ti\ *k*\ Z

.. todo:: pgf/tikz example

.. _interactive-exercises:

Interactive exercises
`````````````````````

.. todo:: section interactive exercises

.. _xrefs:

Cross-references
````````````````

.. todo:: section cross-references

.. _glossary:

Glossary
````````

.. todo:: section glossary

.. _localization:

Localization
------------

.. todo::

  * general words
  * use with only one language

.. seealso::

  * Section :ref:`sections_and_subsections` on how to structure directories
    with multiple languages.
  * Section :ref:`static_files` for translating media files.
  * Section :ref:`content_files` for translating Markdown content.

.. _example-course:

Example course
--------------

There's an example course. It's a comprehensive demonstration of what is
possible with innoConv.

It serves the following purposes:

* Showcase the capabilities and features
* Reference for authors
* Material for automatic software tests

.. note::

  If you want to start compiling content, check out this course and start
  using innoConv right away.

Links
~~~~~

* `Live version <https://tub_base.innocampus.tu-berlin.de/>`_
* `Content source repository <https://gitlab.tu-berlin.de/innodoc/tub_base>`_
