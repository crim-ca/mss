#!/usr/bin/env python
# coding:utf-8

from time import time
import threading
import subprocess
import re
import os
import requests

from VestaRestPackage.app_objects import APP

MSS_CONFIG = APP.config['MSS']
TOKEN_RENEWAL_FREQ = MSS_CONFIG['TOKEN_RENEWAL_FREQ']
TEMP_URL_DEFAULT_VALIDITY = MSS_CONFIG['TEMP_URL_DEFAULT_VALIDITY']
STORAGE_SERVICE_CONTAINER = MSS_CONFIG['STORAGE_SERVICE_CONTAINER']
SWIFT_CONFIG = MSS_CONFIG['SWIFT']

STORAGE_URL_IGNORE_PREFIX_FOR_TEMP_URL = None
if "STORAGE_URL_IGNORE_PREFIX_FOR_TEMP_URL" in MSS_CONFIG:
	STORAGE_URL_IGNORE_PREFIX_FOR_TEMP_URL = MSS_CONFIG['STORAGE_URL_IGNORE_PREFIX_FOR_TEMP_URL']

# Swift credential options to obtain (AUTH_STORAGE and AUTH_TOKEN): 
# For v2.
#    "V2_REMOTE", if we need to connect to a machine on the open stack network and call python-swift client there.
#   "V2_LOCAL", we can call swift auth api from local machine using python-swift client.
# For v1:
#   "V1_LOCAL", we can obtain them from from local machine using curl.

SWIFT_AUTHENTIFICATION_OPTIONS = "V2_REMOTE"
if "SWIFT_AUTHENTIFICATION_OPTIONS" in MSS_CONFIG:
    SWIFT_AUTHENTIFICATION_OPTIONS = MSS_CONFIG["SWIFT_AUTHENTIFICATION_OPTIONS"]

SWIFT_TIMEOUT = MSS_CONFIG.get('SWIFT_TIMEOUT', 5)

def _execute_command(cmd):
    subprocess.check_call(cmd,shell=True)

auth_url = SWIFT_CONFIG['os-auth-url']
tenant = SWIFT_CONFIG['os-tenant-name']
user = SWIFT_CONFIG['os-username']
passwd = SWIFT_CONFIG['os-password']
swift_cmd = "post {container_name}".format(container_name=STORAGE_SERVICE_CONTAINER)
swiftAuthOptions = SWIFT_AUTHENTIFICATION_OPTIONS

if "V2" in swiftAuthOptions:
    region = SWIFT_CONFIG['os-region-name']

    ssh_cmd = ("swift "
               "--os-auth-url '{auth_url}' "
               "--os-tenant-name '{tenant}' "
               "--os-username '{user}' "
               "--os-password '{pw}' "
               "--os-region-name {region} {swift_cmd}".
               format(auth_url=auth_url,
                      tenant=tenant,
                      user=user,
                      pw=passwd,
                      region=region,
                      swift_cmd=swift_cmd))

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
    cmd = ("swift -A '{auth_url}' -U '{tenant}':'{user}' -K '{pw}' {swift_cmd}".
          format(auth_url=auth_url,
                  tenant=tenant,
                  user=user,
                  pw=passwd,
                  swift_cmd=swift_cmd))

out = dict()
args = (cmd,)
thr = threading.Thread(target=_execute_command,
                       args=args)
thr.start()
thr.join(timeout=SWIFT_TIMEOUT)
if thr.is_alive():
    msg = ('Timeout occurred renewing swift token\n{cmd}'
           .format(cmd='Command:\n{cmd}'.format(cmd=cmd)))
    raise Exception(msg)
