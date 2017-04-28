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

# Database name relative to the current application directory
DATABASES = {
    'Invocations': {
        'filename': "/data/service_invocations.db",
        'schema_filename': "../static/service_invocations_schema.sql"},
    'Requests': {
        'filename': "/data/requests.db",
        'schema_filename': "../static/requests_schema.sql"}}

CELERY = {
    'BROKER_URL': "amqp://amqp-server//",
    'CELERY_RESULT_BACKEND': "amqp://",
    'CELERY_TASK_SERIALIZER': "json",
    'CELERY_RESULT_SERIALIZER': "json",
    'CELERY_ACCEPT_CONTENT': ["json"],
    'CELERY_TASK_RESULT_EXPIRES': 7200}

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

WORKER_SERVICES = {
    'transcoder': {
        'route_keyword': 'transcoder',
        'celery_task_name': 'transcoder',
        'celery_queue_name': 'transcoder',
        'name': 'Transcoder service',
        'synopsis': "RESTful service providing my_service.",
        'version': '0.2.8',  # Expected version - will check.
        'institution': 'My Organisation',
        'releaseTime': '2015-01-01T00:00:00Z',
        'supportEmail': 'support@my-organisation.ca',
        'category': "Data Manipulation",
        'researchSubject': "My research subject",
        'tags': "my_service, research",
        'home': "http://localhost/docs/my_service.html",
        'doc': "http://localhost/docs/my_service.html",
        'releasenotes': "http://localhost/docs/my_service.html",
        'support': "http://localhost/docs/my_service.html",
        'source': ",204",
        'tryme': "http://localhost/docs/my_service.html",
        'licence': "http://localhost/docs/my_service.html",
        'provenance': "http://localhost/docs/my_service.html",
        'os_args': {'image': 'transcoder_v_0.2.5',
                    'instance_type': 'm1.large'},
        # Process-request to spawn VM ratio
        'rubber_params': {'spawn_ratio': 0.1}
    }
}

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
