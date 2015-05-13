#!/usr/bin/env python
# coding:utf-8

# -- Standard lib ------------------------------------------------------------
from hashlib import sha1
from time import time
import threading
import commands
import logging
import hmac
import re
import os

# -- 3rd party ---------------------------------------------------------------
from flask import redirect
import requests

# -- Project specific --------------------------------------------------------
from .abstract_storage_backend import AbstractStorageBackend
from .VestaRestPackage.app_objects import APP
from .exceptions import SwiftException

MSS_CONFIG = APP.config['MSS']
TOKEN_RENEWAL_FREQ = MSS_CONFIG['TOKEN_RENEWAL_FREQ']
TEMP_URL_DEFAULT_VALIDITY = MSS_CONFIG['TEMP_URL_DEFAULT_VALIDITY']
STORAGE_SERVICE_CONTAINER = MSS_CONFIG['STORAGE_SERVICE_CONTAINER']
SWIFT_CONFIG = MSS_CONFIG['SWIFT']

# Swift credential options to obtain (AUTH_STORAGE and AUTH_TOKEN): 
# For v2.
#	"V2_REMOTE", if we need to connect to a machine on the open stack network and call python-swift client there.
#   "V2_LOCAL", we can call swift auth api from local machine using python-swift client.
# For v1:
#   "V1_LOCAL", we can obtain them from from local machine using curl.

SWIFT_AUTHENTIFICATION_OPTIONS = "V2_REMOTE"
if "SWIFT_AUTHENTIFICATION_OPTIONS" in MSS_CONFIG:
	SWIFT_AUTHENTIFICATION_OPTIONS = MSS_CONFIG["SWIFT_AUTHENTIFICATION_OPTIONS"]


class SwiftToken(object):
    """
    Handler class for tokens to be used with swift.
    """
    def __init__(self, storage_url=None, auth_token=None):
        self.logger = logging.getLogger(__name__ + ".SwiftToken")
        self.storage_url = storage_url
        self.auth_token = auth_token
        self.expire = int(time() + TOKEN_RENEWAL_FREQ)
        self.logger.debug(u"Creating token at {0}, expires: {1}".
                          format(storage_url, self.expire))

    def is_valid(self):
        """
        Certify token validity.
        """
        self.logger.debug(u"Checking token validity")
        return (self.storage_url is not None and
                self.auth_token is not None and
                self.expire > time())


class SwiftStorageBackend(AbstractStorageBackend):
    def __init__(self):
        self.logger = logging.getLogger(__name__ + ".SwiftStorageBackend")
        self.logger.info(u"Instantiating swift storage backend")
        self.token = None
        self.temp_key = None
        AbstractStorageBackend.__init__(self)
        try:
            self.__renew_swift_token()
        except SwiftException as exc:
            # Cannot do anything else apart logging the error
            # (No request have been done)
            self.logger.error(unicode(exc))

    def __set_temp_key(self, key=STORAGE_SERVICE_CONTAINER):
        self.temp_key = key
        headers = {'X-Auth-Token': self.__get_token().auth_token,
                   'X-Account-Meta-Temp-URL-Key': self.temp_key}

        response = requests.post(self.__get_token().storage_url,
                                 headers=headers,
                                 verify=False)

        if response.status_code != requests.codes.ok:
            response.raise_for_status()

    @staticmethod
    def __async_renew_swift_token(out, cmd):
        out['cmd_output'] = commands.getstatusoutput(cmd)

	def __get_cmd_for_swift_credentials(swiftAuthOptions):
	    auth_url = SWIFT_CONFIG['os-auth-url']
	    tenant = SWIFT_CONFIG['os-tenant-name']
	    user = SWIFT_CONFIG['os-username']
	    passwd = SWIFT_CONFIG['os-password']

		if "V2" in swiftAuthOptions:
		    region = SWIFT_CONFIG['os-region-name']

		    ssh_cmd = ("swift "
		               "--os-auth-url '{auth_url}' "
		               "--os-tenant-name '{tenant}' "
		               "--os-username '{user}' "
		               "--os-password '{pw}' "
		               "--os-region-name {region} {cmd}".
		               format(auth_url=auth_url,
		                      tenant=tenant,
		                      user=user,
		                      pw=passwd,
		                      region=region,
		                      cmd='stat -v'))

			if swiftAuthOptions == "V2_REMOTE":
				cert = os.path.abspath(SWIFT_CONFIG['certificate_filename'])
				token_user = SWIFT_CONFIG['token_server_user']
				token_server = SWIFT_CONFIG['token_server']
				cmd = ('ssh -oStrictHostKeyChecking=no '
				       '-i {cert} {user}@{server} \"{cmd}\"'.
				       format(cert=cert,
				              user=token_user,
				              server=token_server,
				              cmd=ssh_cmd))
			else:
				cmd = ssh_cmd
		else:
			cmd = "swift -A '{auth_url}' -U '{tenant}':'{user}' -K '{pw}' {cmd}".
				format(auth_url=auth_url,
	                      tenant=tenant,
	                      user=user,
	                      pw=passwd,
	                      cmd='stat -v'))

	    out = dict()
	    args = (out, cmd)
	    thr = threading.Thread(target=self.__async_renew_swift_token,
	                           args=args)
	    thr.start()
	    thr.join(timeout=5)
	    if thr.is_alive():
	        msg = ('Timeout occurred renewing swift token\n{cmd}'
	               .format(cmd='Command:\n{cmd}'.format(cmd=cmd)))
	        raise SwiftException(msg)

        return out['cmd_output']

    def __renew_swift_token(self):
        self.logger.info(u"Renewing swift token")

		cmd_output = self.__get_cmd_for_swift_credentials(SWIFT_AUTHENTIFICATION_OPTIONS)

        lines = cmd_output[1].split('\n')
        self.token = SwiftToken()
        for line in lines:
            match = re.search('StorageURL: *(.*)$', line)
            if match:
                self.token.storage_url = match.group(1)
            else:
                match = re.search('Auth Token: *(.*)$', line)
                if match:
                    self.token.auth_token = match.group(1)

        if not self.token.is_valid():
            out = cmd_output[1].replace('\\r\\n', '\r\n')
            t_cmd = 'Command:\n{cmd}'.format(cmd=cmd)
            t_out = '\nOutput:\n{out}'.format(out=out)
            msg = ('Cannot obtain a valid swift token\n{cmd}\n{out}'
                   .format(cmd=t_cmd, out=t_out))

            raise SwiftException(msg)

        # Make sure the temp key is OK each time we renew the token
        self.__set_temp_key()

    def __get_token(self):
        """
        Renew Swift token.
        """
        if self.token is None or not self.token.is_valid():
            self.__renew_swift_token()
        return self.token

    def file_exists(self, filename):
        """
        Check for the existence of a file

        :param filename: The unique document URL
        :type filename: str
        :returns: True if the file exists in the backend
        """
        headers = {'X-Auth-Token': self.__get_token().auth_token}
        url = ('{url}/{container}/{fn}'.
               format(url=self.__get_token().storage_url,
                      container=STORAGE_SERVICE_CONTAINER,
                      fn=os.path.basename(filename)))

        response = requests.head(url, headers=headers, verify=False)
        if response.status_code != requests.codes.ok:
            return False
        return True

    # TODO: Upload as a stream rather than a local copy :
    #  http://docs.python-requests.org/en/latest/user/quickstart/#make-a-request
    #  http://toolbelt.readthedocs.org/en/latest/
    def upload(self, filename):
        """
        Upload the given file to the backend storage

        :param filename: The unique document URL
        :type filename: str
        """
        headers = {'X-Auth-Token': self.__get_token().auth_token,
                   'Content-Type': 'application/octet-stream'}

        url = ('{url}/{container}/{fn}'.
               format(url=self.__get_token().storage_url,
                      container=STORAGE_SERVICE_CONTAINER,
                      fn=os.path.basename(filename)))

        self.logger.info(u"Uploading file {fn} to backend storage at {u}".
                         format(fn=filename, u=url))
        response = requests.put(url,
                                headers=headers,
                                data=open(filename, 'rb'),
                                verify=False)

        if response.status_code != requests.codes.ok:
            response.raise_for_status()

    def download(self, filename):
        """
        Make a flask response containing a redirect to a swift temp url

        :param filename: (String) The unique document URL
        :return: A flask response with the proper redirection
        """
        self.logger.info(u"Getting file {fn}".format(fn=filename))
        return redirect(self.get_temp_url(filename, method='GET'))

    def delete(self, filename):
        """
        Delete a file from swift

        :param filename: (String) The unique document URL
        """
        headers = {'X-Auth-Token': self.__get_token().auth_token}
        url = ('{url}/{container}/{fn}'.
               format(url=self.__get_token().storage_url,
                      container=STORAGE_SERVICE_CONTAINER,
                      fn=os.path.basename(filename)))

        self.logger.info(u"Deleting file {fn}".format(fn=filename))
        response = requests.delete(url, headers=headers, verify=False)
        if response.status_code != requests.codes.ok:
            response.raise_for_status()

    def purge_container(self):
        """
        Remove all objects from the container
        """
        headers = {'X-Auth-Token': self.__get_token().auth_token,
                   'Accept': 'application/json'}

        url = ('{url}/{container}'.
               format(url=self.__get_token().storage_url,
                      container=STORAGE_SERVICE_CONTAINER))

        self.logger.info(u"Removing all objects from {u}".format(u=url))
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code != requests.codes.ok:
            response.raise_for_status()

        file_list = response.json()

        deleted_files = list()
        for file_desc in file_list:
            deleted_files.append(file_desc['name'])
            self.delete(file_desc['name'])

        return deleted_files

    def get_temp_url(self, filename, method='GET',
                     validity_in_secs=TEMP_URL_DEFAULT_VALIDITY):

        expires = int(time() + validity_in_secs)
        storage_url_parts = self.__get_token().storage_url.split('/', 3)
        path = ('/{url}/{container}/{fn}'.
                format(url=storage_url_parts[3],
                       container=STORAGE_SERVICE_CONTAINER,
                       fn=filename))

        # hmac_body = '%s\n%s\n%s' % (method, expires, path)
        hmac_body = '{method}\n{exp}\n{path}'.format(method=method,
                                                     exp=expires,
                                                     path=path)

        sig = hmac.new(self.temp_key, hmac_body, sha1).hexdigest()

        args = 'temp_url_sig={0}&temp_url_expires={1}'.format(sig, expires)
        base_url = ('{url}/{container}/{fn}'.
                    format(url=self.__get_token().storage_url,
                           container=STORAGE_SERVICE_CONTAINER,
                           fn=filename))
        temp_url = '{base_url}?{args}'.format(base_url=base_url, args=args)
        return temp_url
