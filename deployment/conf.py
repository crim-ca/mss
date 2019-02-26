# coding: utf-8

"""
Default configuration values for service gateway package.

Copy this file, rename it if you like, then edit to keep only the values you
need to override for the keys found within.

To have the programs in the package override the values with the values
found in this file, you need to set the environment variable named
"VRP_CONFIGURATION" to the path of your own copy before launching the program.
"""

MY_SERVER_NAME = "vesta-mss"

MONGO_URI = "mongodb://localhost:27017/MSS"

# Defines the list of indexes to be created in MongoDB
# see http://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.create_index
MONGO_COLLECTIONS = {
    'Invocations': [[("service",1),('datetime',-1)]],
    'Requests': ['uuid']
}

# Change to internal volume.
REQUEST_REGISTER_FN = "static/requests.shelve"

# security section. For tests without security, put
SECURITY = {"BYPASS_SECURITY": True}
# SECURITY = {
#     # Needed for workers to call VLB to obtain ressources.
#     'AUTHORISATION_KEY': "aed9yhfapgaegaeg",
#     # Used to configure JSON web token.
#     'JWT': {
#         'JWT_SIGNATURE_KEY': "vJmMvm44x6RJcVXNPy6UDcSfJHOHNHrT1tKpo4IQ4MU=",
#         'JWT_AUDIENCE': "VestaServices",
#         'JWT_ALGORITHM': "HS512",
#         'JWT_DURATION': 600  # The following is specified in seconds.
#     }
# }

# vesta-mss is the name of the mss running inside a docker container
# http://132.217.140.31:9995/status?uuid=b1ac8eba-3545-479a-9219-b4004184a2f4
GET_STORAGE_DOC_REQ_URL = "http://mss/get/{storage_doc_id}"
POST_STORAGE_DOC_REQ_URL = "http://mss/add"

MSS = {
    'SWIFT_AUTHENTIFICATION_OPTIONS': 'V1_LOCAL',
    'SWIFT_REDIRECT_URL': 'http://swift:8080',
    'STORAGE_URL_IGNORE_PREFIX_FOR_TEMP_URL': 'swift',
    'SWIFT': {
        'os-auth-url': 'http://swift:8080/auth/v1.0',
        'os-tenant-name': 'test',
        'os-username': 'tester',
        'os-password': 'crim1Log',
        },

    'STORAGE_SERVICE_CONTAINER': 'DockerMSSMultimedia',

    # Swift token renewal frequency (Twice a day)
    'TOKEN_RENEWAL_FREQ': 43200,

    # Temp url validity (One day)
    'TEMP_URL_DEFAULT_VALIDITY': 86400
    }
