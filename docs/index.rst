.. _mss_home:

Multimedia Storage System documentation
=======================================

.. include:: ../README.rst

User's Guide
------------

Describes the typical usage of the Multimedia Storage System REST API functions.

.. toctree::
   :maxdepth: 3

   user_guide


Package information
-------------------

.. toctree::
   :maxdepth: 2

   install
   authors
   license
   provenance
   source
   release_notes


Source code documentation
-------------------------

This section documents the actual code modules for anyone interested in
interfacing with the code base or to study the code internals.

Code structure
++++++++++++++

- Shared interface between MSS and Service Gateway
- Common software package shared between MSS/Service Gateway and worker
  services, speeding up the development of new worker services.

  - Defines message format and contents along with processing methodology

Package level
+++++++++++++

.. toctree::
   :maxdepth: 2
   :glob:

   src/*


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
