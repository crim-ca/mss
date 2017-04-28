#!/bin/bash
python -m mss.init_swift_container
gunicorn -w 4 -preload -b 0.0.0.0:5000 mss.rest_api:APP --log-config=logging.conf
