#!/usr/bin/env python
# coding:utf-8

# N.B. : Some of these docstrings are written in reSTructured format so that
# Sphinx can use them directly with fancy formatting.

"""
This module defines a REST API for the multimedia storage system as defined by
the CANARIE API specification. See :
https://collaboration.canarie.ca/elgg/file/download/849

Any incoming transcoding request on the REST interface is passed on to the
Celery distributed worker queue and any service workers listening on the
corresponding queue should pick up the request message and initiate their task.

From a code separation perspective this module is in charge of defining the
REST API and use others modules to do the actual job. It also plays the role of
formatting any response that should be sent back in the proper format.
"""

# -- Standard lib ------------------------------------------------------------
import tempfile
import logging
import os

# -- 3rd party ---------------------------------------------------------------
from flask import request
from flask import jsonify
import jinja2

# -- Project specific --------------------------------------------------------
from .VestaRestPackage.request_authorisation import validate_authorisation
from .VestaRestPackage.generic_rest_api import configure_home_route
from .VestaRestPackage.utility_rest import MissingParameterError
from .VestaRestPackage.utility_rest import get_request_url
from .swift_storage_backend import SwiftStorageBackend
from .VestaRestPackage.utility_rest import submit_task
from .VestaRestPackage.utility_rest import log_request
from .VestaRestPackage.utility_rest import uuid_task
from .VestaRestPackage.generic_rest_api import APP
from .exceptions import InvalidConfiguration


# TODO : Re-work the restfulness aspect of this HTTP API.

# The SSM service name is in config file and should be the only one
# if len(APP.config['WORKER_SERVICES'].keys()) != 1:
#     raise InvalidConfiguration('There should be one and only one service '
#                                'configured for the MSS which is Transcoding. '
#                                '(Incomplete configuration?)')

SERVICE_NAME = APP.config['WORKER_SERVICES'].keys()[0]

UPLOAD_FOLDER = tempfile.mkdtemp()

APP.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Add the SSM templates folder to the template loader directories
# (VRP one is used by default)
TEMPLATES_LOADER = jinja2.ChoiceLoader([
    APP.jinja_loader,
    jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),
                                         'templates'))
])
APP.jinja_loader = TEMPLATES_LOADER

STORAGE_BACKEND = SwiftStorageBackend()


@APP.route("/add/<worker_autorization_key>", methods=['POST', 'GET'])
@APP.route("/add", defaults={'worker_autorization_key': None},
           methods=['POST', 'GET'])
def add(worker_autorization_key):
    """
    POST a new file to add into the storage server (file\:form-data)
    GET a temporary public URL from swift to upload a file.

    The file name must be provided as parameter, for example::
    
       /add?filename=name.ext

    :returns: [POST] JSON object with the unique URL of the file.
              [GET] JSON object with the unique URL of the file
              and the URL to make a PUT with the file.
    """
    logger = logging.getLogger(__name__)

    sec = APP.config["SECURITY"]
    validate_authorisation(request, sec, worker_autorization_key)

    if request.method == 'POST':

        files_doc_url = list()
        for file_key in request.files:
            upload_file = request.files[file_key]
            ufn = upload_file.filename
            filename = STORAGE_BACKEND.get_unique_filename(ufn)

            log_request(SERVICE_NAME,
                        '/add : POST file at : {0}'.format(filename))

            # TODO : Could be more efficient to use the already existing file
            # held by flask rather than doing a copy here
            full_filename = os.path.join(APP.config['UPLOAD_FOLDER'], filename)
            upload_file.save(full_filename)

            logger.info(u"Adding file {fn} to storage server".
                        format(fn=filename))
            STORAGE_BACKEND.upload(full_filename)

            logger.info(u"Destroying local copy of the uploaded document :"
                        u" {0}".format(full_filename))
            os.remove(full_filename)

            files_doc_url.append({upload_file.filename:
                                  {'storage_doc_id': filename}})

        if len(files_doc_url) == 0:
            logger.warning(u"Could not upload file")
            return "Failed"
        if len(files_doc_url) == 1:
            return jsonify(files_doc_url[0].itervalues().next())

        return jsonify(files_doc_url)

    else:
        if 'filename' not in request.args:
            raise MissingParameterError('GET', '/add', 'filename')

        rfn = request.args.get('filename', '')
        filename = STORAGE_BACKEND.get_unique_filename(rfn)
        upload_url = STORAGE_BACKEND.get_temp_url(filename, 'PUT')
        logger.info(u"Adding file {fn} to storage server".
                    format(fn=rfn))

        log_request(SERVICE_NAME,
                    '/add : Get temp url to upload at : {0}'.
                    format(filename))

        return jsonify({'storage_doc_id': filename, 'upload_url': upload_url})


@APP.route("/delete/<storage_doc_id>", methods=['POST'])
def delete(storage_doc_id):
    """
    POST a delete request for a given document.

    :param storage_doc_id: The unique document id of the file to delete.
    """
    logger = logging.getLogger(__name__)
    log_request(SERVICE_NAME,
                '/delete : Delete file : {0}'.format(storage_doc_id))
    logger.info(u"Deleting file with id %s", storage_doc_id)
    STORAGE_BACKEND.delete(storage_doc_id)
    return jsonify({'deleted': True})


@APP.route("/get/<storage_doc_id>")
def get(storage_doc_id):
    """
    GET the file associated with the given storage_doc_id

    :param storage_doc_id: The unique document id of the file to get.
    """
    logger = logging.getLogger(__name__)
    log_request(SERVICE_NAME,
                '/get : Download file : {0}'.format(storage_doc_id))

    logger.info(u"Obtaining file with id {i}".format(i=storage_doc_id))
    return STORAGE_BACKEND.download(storage_doc_id)


@APP.route("/transcode", methods=['POST'])
@APP.route("/transcode/<storage_doc_id>", methods=['POST'])
def transcode(storage_doc_id=None):
    """
    POST a transcoding request through a form.

    :param storage_doc_id: The unique document id of the file to transcode.
                           If not provided, a doc_url parameter must be
                           submitted in the request.
    :returns: JSON object with the task uuid or error response.
    """
    logger = logging.getLogger(__name__)

    validate_authorisation(request, APP.config["SECURITY"])

    # request.values combines values from args and form
    if 'thumbnail_timecode' in request.values:
        thumbnail_timecode = request.values['thumbnail_timecode']
    else:
        thumbnail_timecode = None

    logger.info(u"Received a transcoding request for {i}".
                format(i=storage_doc_id))

    upload_url = get_request_url('POST_STORAGE_DOC_REQ_URL',
                                 {'storage_doc_id': storage_doc_id})
    task_misc_data = {'upload_url': upload_url,
                      'thumbnail_timecode': thumbnail_timecode}

    logger.debug("misc_data is : %s", task_misc_data)
    return submit_task(storage_doc_id,
                       'transcoder',
                       service_route=SERVICE_NAME,
                       misc=task_misc_data)


@APP.route("/<any(status,cancel):task>")
def uuid_task_route(task):
    """
    Get the status or cancel a task identified by a uuid.

    :param task: status or cancel
    :returns: JSON object with latest status or error response.
    """
    logger = logging.getLogger(__name__)
    logger.info(u"Got {t} request".format(t=task))
    return uuid_task(task, SERVICE_NAME)


@APP.route("/stream/<storage_doc_id>")
def stream(storage_doc_id):
    """
    GET the streaming server URL for a given unique URL.

    :param storage_doc_id: The unique document id of the file to stream.
    :returns: JSON object with a valid URL from which the video can be streamed
    """
    logger = logging.getLogger(__name__)
    log_request(SERVICE_NAME,
                '/stream : GET stream url for : {0}'
                .format(storage_doc_id))

    logger.info(u"Got stream request for {i}".format(i=storage_doc_id))
    return jsonify({'stream_url':
                    STORAGE_BACKEND.get_temp_url(storage_doc_id,
                                                 method='GET')})


if __name__ != "__main__":
    configure_home_route()
