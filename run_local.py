#!/usr/bin/env python
# coding: utf-8

"""
Simple helper script to load application in development mode.
"""

# -- Standard lib ------------------------------------------------------------
import logging.config
import optparse
import logging
import os

# -- Project specific --------------------------------------------------------
from mss.__meta__ import __version__
from mss.rest_api import APP

THIS_DIR = os.path.abspath(os.path.dirname(__file__))

if __name__ == '__main__':
    LOG_CONF_FN = os.path.join(THIS_DIR, 'mss', 'logging.conf')

    PARSER = optparse.OptionParser(version=__version__)

    PARSER.add_option('-p', '--port', dest='port', type=int, default=5000)
    PARSER.add_option('-d', '--debug', dest='debug', action="store_true",
                      default=False)
    PARSER.add_option("-l", "--logconf",
                      action='store',
                      default=LOG_CONF_FN,
                      dest='logging_conf_fn',
                      help='Set logging configuration filename')

    OPTS, ARGS = PARSER.parse_args()

    # logging.config.fileConfig(OPTS.logging_conf_fn)
    logging.basicConfig(level=logging.DEBUG)

    LOGGER = logging.getLogger(__name__)
    LOGGER.info("Using log configuration file {c}".
                format(c=OPTS.logging_conf_fn))

    APP.run(host='0.0.0.0', port=OPTS.port, debug=OPTS.debug)
