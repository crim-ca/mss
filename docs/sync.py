#!/usr/bin/env python

"""
Send contents to server.
"""

from subprocess import check_call
from urlparse import urljoin
from shlex import split


from conf import __version__ as VERSION

DOC_DESTINATION = ("centos@services.vesta.crim.ca:"
                   "/usr/share/nginx/html/docs/mss/")


def norm_perms():
    """
    Normalize permissions in the build directory.
    """
    cmd = split("find _build/html/ -type d -exec chmod o+x '{}' ';'")
    check_call(cmd)
    cmd = split("chmod -R o+r _build/html/")
    check_call(cmd)


def send_static(version=VERSION):
    """
    Send static site on server.
    """
    cmd = split("rsync -av _build/html/")
    cmd += [urljoin(DOC_DESTINATION, version)]
    check_call(cmd)


def main():
    """
    Command line entry point.
    """
    norm_perms()
    send_static()


if __name__ == '__main__':
    main()
