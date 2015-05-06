#!/usr/bin/env python
# coding:utf-8

# -- Standard lib ------------------------------------------------------------
import hashlib
import time

ALPHABET_62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALPHABET_16 = "0123456789abcdef"
ALPHABET_62_PADDING = 22
ALPHABET_16_PADDING = 32


class AbstractStorageBackend:
    def __init__(self):
        pass

    def base_encode(self, num,
                    alphabet=ALPHABET_62,
                    padding=ALPHABET_62_PADDING):
        """
        Encode a number in Base X

        `num`: The number to encode
        `alphabet`: The alphabet to use for encoding
        """
        if num == 0:
            return alphabet[0]
        arr = []
        base = len(alphabet)
        while num:
            rem = num % base
            num = num // base
            arr.append(alphabet[rem])
        arr.reverse()

        if len(arr) > padding:
            raise OverflowError("{val} exceeds 128bits value")

        return ''.join(arr).zfill(padding)

    def base_decode(self, string, alphabet=ALPHABET_16):
        """
        Decode a Base X encoded string into the number

        Arguments:
        - `string`: The encoded string
        - `alphabet`: The alphabet to use for encoding
        """
        base = len(alphabet)
        strlen = len(string)
        num = 0

        idx = 0
        for char in string:
            power = (strlen - (idx + 1))
            num += alphabet.index(char) * (base ** power)
            idx += 1

        return num

    # TODO : Couldn't this simply be a call to tempfile.NamedtemporaryFile ?
    def get_unique_filename(self, filename):
        """
        Create a unique filename.
        """
        ext = ''
        if '.' in filename:
            ext = '.' + filename.rsplit('.', 1)[1]
        while True:
            m = hashlib.md5()
            m.update(filename)
            m.update(str(time.time() * 1000))
            digest = m.hexdigest()
            uni_filename = self.base_encode(self.base_decode(digest))
            uni_filename += ext
            if not self.file_exists(uni_filename):
                return uni_filename

    def file_exists(self, filename):
        """
        Check for the existence of a file

        :param filename: (String) The unique document URL
        :return: True if the file exists in the backend
        """
        msg = "Function «file_exists» is meant to be overridden"
        raise NotImplementedError(msg)

    def upload(self, filename):
        """
        Upload the given file to the backend storage

        :param filename: (String) The unique document URL
        """
        msg = "Function «upload» is meant to be overridden"
        raise NotImplementedError(msg)

    def download(self, filename):
        """
        Make a flask response containing the file to download

        :param filename: (String) The unique document URL
        :return: A flask response with the file to download
        """
        msg = "Function «download» is meant to"" be overridden"
        raise NotImplementedError(msg)
