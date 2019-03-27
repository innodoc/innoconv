What is innoConv?
=================

innoConv is a converter for educational content.

It transforms content into an intermediate format (JSON) that can be displayed
with a :ref:`innodoc-compatible viewer <viewers>`.

Course structure
----------------

TODO

- :file:`toc.md`
- language directories
  - chapters and sections in sub-directories
  - :file:`content.md`

Example course
--------------

There's an example course. It's a comprehensive demonstration of what is
possible with innoConv.

It serves the following purposes:

* Showcase the capabilities and features
* Reference for course authors
* Case for automatic software tests

It can also serve as a starting point for trying out innoConv before writing
your own content.

Links
~~~~~

* `Demo course live version <https://tub_base.innocampus.tu-berlin.de/>`_
* `Content source repository <https://gitlab.tu-berlin.de/innodoc/tub_base>`_

innoDoc
-------

innoConv is one part in a software package called
`innoDoc <https://www.innocampus.tu-berlin.de/en/projects/innodoc/>`_.

.. image:: figures/overview.*

.. _viewers:

Viewers
~~~~~~~

At the moment there are two viewers in development.

innodoc-webapp
  `React-based HTML5 web application <https://gitlab.tu-berlin.de/innodoc/innodoc-webapp>`_

innodoc-app
  `React Native-based Smartphone App <https://gitlab.tu-berlin.de/innodoc/innodoc-app>`_
