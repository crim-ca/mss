==============================
NEP-143-3 Stockage de fichiers
==============================


This package offers a multimedia file storage system residing behind a REST API. 

The different functions offered by this code base are the following:

* Provide a unified CANARIE REST interface for a collection of multimedia
   files
* Provide an asynchronous API to transcode documents through the Celery
  interface.

This solution relies on the `Celery
<http://celery.readthedocs.org/en/latest/index.html>`_ distributed task queue
and `RabbitMQ <http://www.rabbitmq.com/>`_ messaging broker to dispatch
processing requests. Also, the REST interface uses the `Flask
<http://flask.pocoo.org/>`_ WEB framework.

-------
LICENSE
-------

see https://github.com/crim-ca/mss/tree/master/THIRD_PARTY_LICENSES.rst


------------
Installation
------------

You can use the `pip
<https://pip.readthedocs.org/en/latest/reference/pip_install.html>`_ utility to
install this package. One way of doing that is by pointing pip directly to the
directory containing the setup.py file such as::

   pip install .

This will install the mss along with program entry points for
various utilities.

A good practise might be to make use of a `virtual environment
<https://virtualenv.pypa.io/en/latest/>`_ in which all the
dependencies will be installed through pip. 

Tests were conducted on Python 2.6.x and should normally worker under version
2.7.

Usage
-----

For validation purposes, usage is as follows::

   python run_local.py --help

This command can launch a built-in Flask WEB server. The
«-d» options launches the WEB server in debug mode. Debug mode is useful for
automatic reloading of code and stack trace forwarding. See the Flask
documentation for more information.

.. warning::

   The REST interface in run_local / debug mode uses a built-in Web Server. While
   this Web Server is useful for a closed environment, it is not recommended as a
   Web Server for a production environment. Care should be taken to configure a
   `WSGI <http://wsgi.readthedocs.org/en/latest/index.html>`_ gateway to a
   production-ready WebServer such as `Apache <http://httpd.apache.org/>`_ or
   `GUnicorn <http://gunicorn.org/>`_ behind a reverse-proxy server such as
   NGinx.
