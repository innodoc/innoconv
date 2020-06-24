What is innoConv?
=================

*innoConv is a converter for educational content.*

The software transforms source content into an intermediate
`JSON <https://www.json.org/>`_ representation that can be displayed with the
help of an :ref:`innodoc-compatible viewer <viewers>`.

It takes plain-text files as a source. These are written in the
`Markdown language <https://daringfireball.net/projects/markdown/>`_ and
stored in a particular
:ref:`directory structure <directory_and_file_structure>` reflecting the
sections and subsections of the work.

.. seealso::

  Check out the :ref:`addtional documentation <additional_documentation>` to
  see how a real course looks like.

Features
--------

Common features as basic text formatting, links, tables, lists, etc. are
already provided by Markdown out-of-the-box.

While staying as close to traditional Markdown as possible innoConv supports
a variety of additional constructs. Many of them are targeted specifically at
the creation of educational content.

These include

* Localization
* Math formulas
* Images and videos
* Interactive exercises
* Vector graphics
* Table of contents
* Inter-section references
* Index

innoDoc
-------

innoConv is a part in the software package
`innoDoc <https://www.innocampus.tu-berlin.de/en/projects/innodoc/>`_. It
handles the translation of source content to the an intermediate JSON
represenation.

.. figure:: figures/overview.*
  :alt: innoDoc overview
  :align: center

  Overview of the innoDoc software architecture.

innoConv does neither have any business with how content is displayed nor
helps in its creation. Instead it leaves these tasks completely to others in
the processing chain.

.. seealso::

  See section :doc:`Content creation <content-creation>` for a in-depth
  discussion on how to write course content.

.. _viewers:

Viewers
~~~~~~~

At the moment there are two viewers in development.

innodoc-webapp
  `React-based HTML5 web application <https://gitlab.tu-berlin.de/innodoc/innodoc-webapp>`_

innodoc-app
  `React Native-based Smartphone App <https://gitlab.tu-berlin.de/innodoc/innodoc-app>`_

.. note::

  Configuration and deployment of viewers is not the scope of this document.
  Please refer to the respective documentation.
