"""
@file
@brief Encryption fucntionalities

Inspired from `AES encryption of files in Python with PyCrypto <http://eli.thegreenplace.net/2010/06/25/aes-encryption-of-files-in-python-with-pycrypto>`_

.. versionadded:: 1.3
"""
import random
import sys
import os
import struct


if sys.version_info[0] == 2:
    from StringIO import StringIO as StreamIO
else:
    from io import BytesIO as StreamIO


class EncryptionError(Exception):
    """
    raised if an issue happen during encryption
    """
    pass


def open_input_output(filename, out_filename=None):
    """
    convert filename and out_filename as streams

    @param      filename        bytes or filename or BytesIO
    @param      out_filename    BytesIO or filename or None
    @return                     in_size, in_close, in_stream, out_close, out_return, out_stream
    """
    # input
    typstr = str  # unicode #
    if isinstance(filename, typstr):
        if not os.path.exists(filename):
            raise FileNotFoundError(filename)
        st = open(filename, "rb")
        close = True
        filesize = os.path.getsize(filename)
    elif isinstance(filename, StreamIO):
        st = filename
        close = False
        filesize = len(st.getvalue())
    else:
        st = StreamIO(filename)
        close = False
        filesize = len(filename)

    # output
    if out_filename is None:
        sto = StreamIO()
        ret = True
        out_close = False
    elif isinstance(out_filename, StreamIO):
        sto = out_filename
        ret = False
        out_close = False
    else:
        sto = open(out_filename, "wb")
        ret = False
        out_close = True

    return filesize, close, st, out_close, ret, sto


def close_input_output(in_size, in_close, in_stream, out_close, out_return, out_stream):
    """
    takes the output of @see fn open_input_output and closes streams
    and return expected values

    @param      in_size         size of input
    @param      in_close        should we close the input stream
    @param      in_stream       input stream
    @param      out_close       should we close the output stream
    @param      out_return      should we return something
    @param      out_stream      output stream
    @return                     None or content of output stream
    """
    if in_close:
        in_stream.close()

    if out_close:
        if out_return:
            raise EncrpytionError("incompability")
        out_stream.close()

    if out_return:
        return out_stream.getvalue()


def encrypt_stream(key, filename, out_filename=None, chunksize=2 ** 18):
    """
    Encrypts a file using AES (CBC mode) with the given key.

    @param      key             The encryption key - a string that must be
                                either 16, 24 or 32 bytes long. Longer keys
                                are more secure.

    @param      filename        bytes or Name of the input file
    @param      out_filename    if None, the returns bytes

    @param      chunksize       Sets the size of the chunk which the function
                                uses to read and encrypt the file. Larger chunk
                                sizes can be faster for some files and machines.
                                chunksize must be divisible by 16.

    @return                     filename or bytes

    The function relies on module `pycrypto <https://pypi.python.org/pypi/pycrypto>`_
    and algoritm `AES <https://fr.wikipedia.org/wiki/Advanced_Encryption_Standard>`_.
    """
    from Crypto.Cipher import AES

    in_size, in_close, in_stream, out_close, out_return, out_stream = open_input_output(
        filename, out_filename)

    ksize = {16, 32, 64, 128, 256}
    if len(key) not in ksize:
        raise EncryptionError(
            "len(key)=={0} should be of length {1}".format(len(key), str(ksize)))

    iv = bytes([random.randint(0, 0xFF) for i in range(16)])
    encryptor = AES.new(key, AES.MODE_CBC, iv)

    out_stream.write(struct.pack('<Q', in_size))
    out_stream.write(iv)

    while True:
        chunk = in_stream.read(chunksize)
        if len(chunk) == 0:
            break
        elif len(chunk) % 16 != 0:
            chunk += b' ' * (16 - len(chunk) % 16)

        out_stream.write(encryptor.encrypt(chunk))

    return close_input_output(in_size, in_close, in_stream, out_close, out_return, out_stream)


def decrypt_stream(key, filename, out_filename=None, chunksize=3 * 2 ** 13):
    """
    Decrypts a file using AES (CBC mode) with the given key.

    @param      key             The encryption key - a string that must be
                                either 16, 24 or 32 bytes long. Longer keys
                                are more secure.

    @param      filename        bytes or Name of the input file
    @param      out_filename    if None, the returns bytes

    @param      chunksize       Sets the size of the chunk which the function
                                uses to read and encrypt the file. Larger chunk
                                sizes can be faster for some files and machines.
                                chunksize must be divisible by 16.

    @return                     filename or bytes
    """
    from Crypto.Cipher import AES

    in_size, in_close, in_stream, out_close, out_return, out_stream = open_input_output(
        filename, out_filename)

    origsize = struct.unpack('<Q', in_stream.read(struct.calcsize('Q')))[0]
    iv = in_stream.read(16)
    decryptor = AES.new(key, AES.MODE_CBC, iv)

    while True:
        chunk = in_stream.read(chunksize)
        if len(chunk) == 0:
            break
        out_stream.write(decryptor.decrypt(chunk))
        out_stream.truncate(origsize)

    return close_input_output(in_size, in_close, in_stream, out_close, out_return, out_stream)
