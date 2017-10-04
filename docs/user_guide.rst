.. _common_rest_interface:

Multimedia Storage Service interface documentation
==================================================


Purpose
-------

The Multimedia Storage Service is essentially an File object store and a
Gateway from an HTTP REST interface to Celery/AMQP interface for file
transformation Services (e.g. transcoding).

This document describes the WEB service interfaces that are common for each
VESTA service which can be exposed by the current Service Gateway.

It shows how a service can be used, the standard response types
and how to handle exceptions.

.. overview ---------------------------------------------------------------
.. include:: ../mss/VestaRestPackage/docs/ug_overview.rst

Methods
-------

Most methods are supplied my an underlying package which offers base methods to
control Service workers, including the basic routes required by the CANARIE
Service API.

The Multimedia Storage Service builds on top of these methods and offers more
specific functionalities for it's purposes. 



Multimedia Storage Service method sets
++++++++++++++++++++++++++++++++++++++

The Multimedia File Storage REST interface is used to upload/download/stream
multimedia files but also to provide a transcoding service that will generate
documents that can be used to perform automatic annotation requests or content
streaming.

It covers:

* <Base URI>/add
* <Base URI>/delete
* <Base URI>/get
* <Base URI>/stream
* <Base URI>/status

Where *<Base URI>* will be the server root.


.. _add_method:

add
~~~

To add a video to file server using one of two methods. A traditional POST can
be performed, but it will imply an upload to the Multimedia File Storage
service server and then a second upload to the real backend file server. A GET
can also be performed, and the received URL will allow a direct upload to the
file server.


Using GET
`````````

This method uses HTTP GET.


Parameters:

:filename: Filename for which an upload URL must be obtained.


Return value:

The service returns a JSON structure containing a temporary «upload_url» that
can be used to upload the document directly to the file server such as:

.. code-block:: json

   {
       "storage_doc_id": "5hEK1ToPWHVhE3Irje5KRq.avi", 
       "upload_url":"https://swift-qc.dair-atir.canarie.ca:8080/v1/AUTH_054956644df74c3b988ecfdb115a145c/VestaServiceStorageMultimedia/5hEK1ToPWHVhE3Irje5KRq.avi?temp_url_sig=41cbdc78cddf0418821331515871a7a61b9b2137&temp_url_expires=1410465382"
   }


:storage_doc_id: The key to access the document from the file server.
:upload_url: A temporary URL which is valid to upload a file using the PUT HTTP
   method and using *content-type application/octet-stream*.


Examples:

URL form:

.. code-block:: bash

   <Base URI>/add?filename=video.avi


Example of requests with the curl utility:

.. code-block:: bash

   curl -X PUT --data-binary "@video.avi" "https://swift-qc.dair-atir.canarie.ca:8080/\
       v1/AUTH_054956644df74c3b988ecfdb115a145c/VestaServiceStorageMultimedia/\
       5hEK1ToPWHVhE3Irje5KRq.avi?temp_url_sig=41cbdc78cddf0418821331515871a7a61b9b2137&temp_url_expires=1410465382"


Using POST
``````````

This method uses HTTP POST.


Parameters:

:file: The file which should be added to the file server.

Return value:

The service returns a JSON structure containing a «doc_url» identifying the
document on the file server:

.. code-block:: json

   {
       "storage_doc_id": "5hEK1ToPWHVhE3Irje5KRq.avi"
   }

:storage_doc_id: A value which can then be used to perform other operations
   documented throughout this documentation.


Examples:

URL form:

.. code-block:: bash

   <Base URI>/add?file=video.avi

Example of requests with the curl utility:

.. code-block:: bash

   curl -F "file=@video.avi" <Base URI>/add



delete
~~~~~~

To delete a document. 

This method uses HTTP POST.


Parameters:

:storage_doc_id: The document identifier returned by the :ref:`add method
   <add_method>`. 


Return value:

The deletion will be done and a JSON structure indicating success will be
returned to the request.


Examples:

URL form:

.. code-block:: bash

   <Base URI>/delete/<storage_doc_id>


get
~~~

To download a document.

This method uses HTTP GET. 


Parameters:

:storage_doc_id: The document identifier returned by the :ref:`add method
   <add_method>`. 


Return value:

The services will redirect the request to the file server and initiate a direct
download of the document.


Examples:

URL form:

.. code-block:: bash

   <Base URI>/get/<storage_doc_id>


stream
~~~~~~

To obtain a URL from which the video can be streamed directly.

This method uses HTTP GET. 


Parameters:

:storage_doc_id: The document identifier returned by the :ref:`add method
   <add_method>`. 


Return value:

The service returns a JSON structure containing a temporary «stream_url» from
which a video can be streamed:

.. code-block:: json

   {
       "stream_url": "https://swift-qc.dair-atir.canarie.ca:8080/v1/AUTH_054956644df74c3b988ecfdb115a145c/VestaServiceStorageMultimedia/5hEK1ToPWHVhE3Irje5KRq.avi?temp_url_sig=ba1f6d9c9c513d8befe2360acdcc198c4f87f5a4&temp_url_expires=1410531262"
   }


Examples:

URL form:

.. code-block:: bash

   <Base URI>/stream/<storage_doc_id>


.. Info route ----------------------------------------------------
.. include:: ../mss/VestaRestPackage/docs/ug_info_route.rst


.. CANARIE API ---------------------------------------------------
.. include:: ../mss/VestaRestPackage/docs/ug_canarie_api.rst


.. Error codes section ===========================================
.. include:: ../mss/VestaRestPackage/docs/ug_error_codes_preamble.rst


.. Core error codes ----------------------------------------------
.. include:: ../mss/VestaRestPackage/docs/ug_core_error_codes.rst


.. VRP error codes -----------------------------------------------
.. include:: ../mss/VestaRestPackage/docs/ug_vrp_error_codes.rst


.. Service error codes -------------------------------------------
.. include:: ../mss/VestaRestPackage/docs/ug_worker_services_error_codes.rst


.. MSS error codes -----------------------------------------------
.. include:: ../mss/VestaRestPackage/docs/ug_mss_error_codes.rst
