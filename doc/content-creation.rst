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

  This section will only give an overview on how to structure your content. It
  will not provide an exhaustive list of formatting options.

  Please refer to the
  :ref:`addtional documentation <additional_documentation>`. It offers more
  detailed information on how to create content with innoDoc.

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

.. _manifest_file:

The manifest file
~~~~~~~~~~~~~~~~~

The root directory is home to the :file:`manifest.yml` file. It is used to
store meta information about your content, like the title, the languages and so
on. It is written in `YAML format <https://yaml.org/>`_.

.. code-block:: yaml
  :caption: A minimal example for a content manifest.

  title:
    en: Example course
    de: Beispielkurs
  languages: en,de

.. note::

  If your content uses just one language, you will still need to list the
  language here.

.. _directory_and_file_structure:

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

The names of the directories determine the section order. They are sorted
alphanumerically. Therefore it's advisable to use a numerical prefix (e.g.
``01-section``).

The directory name itself is the ID for the section and can
be used to create cross-references from one part in the the text to another.
Also, they are used to form :abbr:`URLs (Uniform Resource Locator)`.

.. note::
  While technically not strictly required, for convenience it's advisable to
  limit directory names to characters, numbers, hyphen and underscore
  (``a-z``, ``0-9``, ``-`` and ``_``).

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

Custom pages
````````````

A course can also include custom pages that are not part of the section
structure. You can define pages by adding them to the ``pages`` key of the
:ref:`manifest file <manifest_file>`. You need to define an ID, optionally an
icon and can choose if the page should show up in the navigation and footer
part of the viewer.

.. code-block:: yaml

  pages:
    - id: about
      icon: info-circle
      linked: [nav, footer]

For every page you need to provide a content file in each language. It uses
the page ID as the name (e.g. :file:`about.md`). The content file is
placed in the :file:`_pages` directory inside the language folder.

Pages also need a YAML header like described in
:ref:`sections_and_subsections`.

Example directory structure
```````````````````````````

.. code-block:: text
  :caption: Example directory structure for two languages.

  root
  ├── manifest.yml
  ├── en
  |   ├── _pages
  |   |   ├── about.md
  |   |   └── …
  |   ├── content.md
  |   ├── 01-part
  |   |   ├── content.md
  |   |   ├── 01-section
  |   |   |   └── content.md
  |   |   └── …
  |   └── …
  └── de
      ├── _pages
      |   ├── about.md
      |   └── …
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

The directory :file:`_static` is used for placing static files such as images
and videos.

The directory exists under the root and can also be placed inside a language
folder for content that needs to be localized. The converter will  prefer files
from the localized folder.

.. code-block:: text
  :caption: Locations for static files.

  root
  ├── _static
  |   ├── chart.svg
  |   └── image.png
  ├── en
  |   └── _static
  |       └── video.mp4
  └── de
      └── _static
          └── video.mp4

*For the sake of clarity other needed files and directories are omitted in this
listing.*

.. _additional_documentation:

Additional documentation
------------------------

For more detailed instructions including examples on how to author content
refer to the innoDoc example course. It features in-depth descriptions on all
content elements and the general course structure.

.. note::

  If you want to start compiling content, check out the source code and start
  using innoConv right away.

Links
~~~~~

* `innoDoc example course <https://veundmint.innocampus.tu-berlin.de/>`_
* `Source repository <https://gitlab.tu-berlin.de/innodoc/tub_base>`_
