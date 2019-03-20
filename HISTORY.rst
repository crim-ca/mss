.. :changelog:


History
=======

1.8.2
-----

* Updated VestaRestPackage to 1.9.3
* Added MSS.SWIFT_TIMEOUT configuration variable


1.8.1
-----

* Updated VestaRestPackage to 1.9.1


1.8.0
-----
 
* No longer provides transcoding features.


1.7.1
-----
 
* Use version 1.7.4 of VRP.


1.7.0
-----
 
* Add delete route.


1.6.1
-----

* Bug fix for malformed "misc" structure used for transcoding.


1.6.0
-----

* First packaged release
* Deployment configuration factored out of package


1.5.0
-----

* Add support for WEBM videos.
* Errors handling is completed, see the documentation below for more details.
* More logs.
* Normalise some fields in the result structure.


1.4.0
-----

* To avoid confusion the service returns a JSON structure containing a
  storage_doc_id rather than a doc_url.
* Queue will expire in 2 hours : Add Status EXPIRED when a queue is no longer
  available.
* Task UUID are stored using a method that supports concurrency.
* The transcode method also gives the video length and framerate.


1.3.0
-----

* New versioning scheme.


1.2.0
-----

* Add a /cancel function to stop a running task.


1.1.0
-----

* The transcode and status functions operate using a task uuid like the Load
  Balancer interface rather than operating on the doc_url as id.
