.. _mss_intro:

NEP-143-3 Multimedia storage system
===================================


This package offers a multimedia file storage system (MSS) with a
REST API. 

.. _mss_overview:

Overview
--------

The different functions offered by this code base are the following:

* Provide a unified CANARIE REST interface for a collection of multimedia
  files
* Provide an asynchronous API to transcode documents through the Celery
  interface.

The documentation for this project can be found `here
<http://services.vesta.crim.ca/docs/mss/latest/>`_ .


Infrastructure Overview
-----------------------

This solution relies on the `Celery
<http://celery.readthedocs.org/en/latest/index.html>`_ distributed task queue
and `RabbitMQ <http://www.rabbitmq.com/>`_ messaging broker to dispatch
processing requests. Also, the REST interface uses the `Flask
<http://flask.pocoo.org/>`_ WEB framework.


Basic Usage
-----------

Interface instantiation
+++++++++++++++++++++++

.. note:: Before starting the application, one must apply his own configuration
          values, see :ref:`configuration` section.

For validation purposes, usage is as follows::

   python run_local.py --help

This command can launch a built-in Flask WEB server. The
«-d» options launches the WEB server in debug mode. Debug mode is useful for
automatic reloading of code and stack trace forwarding. See the Flask
documentation for more information.

.. Warning::

   The REST interface in run_local / debug mode uses a built-in Web Server.
   While this Web Server is useful for a closed environment, it is not
   recommended as a Web Server for a production environment. Care should be
   taken to configure a `WSGI
   <http://wsgi.readthedocs.org/en/latest/index.html>`_ gateway to a
   production-ready WebServer such as `Apache <http://httpd.apache.org/>`_ or
   `GUnicorn <http://gunicorn.org/>`_ behind a reverse-proxy server such as
   NGinx.
