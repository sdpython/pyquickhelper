"""
@file
@brief Encryption functionalities.

Inspired from `AES encryption of files in Python with PyCrypto
<http://eli.thegreenplace.net/2010/06/25/aes-encryption-of-files-in-python-with-pycrypto>`_
"""
import random
import os
import struct
import base64
from io import BytesIO as StreamIO


class EncryptionError(Exception):
    """
    raised if an issue happen during encryption
    """
    pass


def open_input_output(filename, out_filename=None):
    """
    Converts *filename* and *out_filename* as streams.

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
    Takes the output of @see fn open_input_output and closes streams
    and return expected values.

    @param      in_size         size of input
    @param      in_close        should it close the input stream
    @param      in_stream       input stream
    @param      out_close       should it closes the output stream
    @param      out_return      should it returns something
    @param      out_stream      output stream
    @return                     None or content of output stream
    """
    if in_close:
        in_stream.close()

    if out_close:
        if out_return:
            raise EncryptionError("incompability")
        out_stream.close()

    if out_return:
        return out_stream.getvalue()
    else:
        return None


def get_encryptor(key, algo="AES", chunksize=2 ** 24, **params):
    """
    Returns an encryptor with method encrypt and decrypt.

    @param      key         key
    @param      algo        AES or fernet
    @param      chunksize   Fernet does not allow streaming
    @param      params      additional parameters
    @return                 encryptor, origsize
    """
    if algo == "fernet":
        from cryptography.fernet import Fernet
        if hasattr(key, "encode"):
            # it a string
            bkey = key.encode()
        else:
            bkey = key
        bkey = base64.b64encode(bkey)
        encryptor = Fernet(bkey)
        origsize = None
        chunksize = None
    elif algo == "AES":
        from Cryptodome.Cipher import AES
        ksize = {16, 32, 64, 128, 256}
        chunksize = chunksize  # pylint: disable=W0127
        if len(key) not in ksize:
            raise EncryptionError(
                "len(key)=={0} should be of length {1}".format(len(key), str(ksize)))
        if "out_stream" in params:
            iv = bytes([random.randint(0, 0xFF) for i in range(16)])
            params["out_stream"].write(struct.pack('<Q', params["in_size"]))
            params["out_stream"].write(iv)
            encryptor = AES.new(key, AES.MODE_CBC, iv)
            origsize = params["in_size"]
        else:
            origsize = struct.unpack(
                '<Q', params["in_stream"].read(struct.calcsize('Q')))[0]
            iv = params["in_stream"].read(16)
            encryptor = AES.new(key, AES.MODE_CBC, iv)  # decryptor
    else:
        raise ValueError("unknown algorithm: {0}, should be in {1}".format(
            algo, ["fernet", "AES"]))
    return encryptor, origsize, chunksize


def encrypt_stream(key, filename, out_filename=None, chunksize=2 ** 18, algo="AES"):
    """
    Encrypts a file using AES (CBC mode) with the given key.
    The function relies on module :epkg:`pycrypto`, :epkg:`cryptography`,
    algoritm `AES <https://fr.wikipedia.org/wiki/Advanced_Encryption_Standard>`_,
    `Fernet <http://cryptography.readthedocs.org/en/latest/fernet/>`_.

    @param      key             The encryption key - a string that must be
                                either 16, 24 or 32 bytes long. Longer keys
                                are more secure. If the data to encrypt is in bytes,
                                the key must be given in bytes too.

    @param      filename        bytes or Name of the input file
    @param      out_filename    if None, the returns bytes

    @param      chunksize       Sets the size of the chunk which the function
                                uses to read and encrypt the file. Larger chunk
                                sizes can be faster for some files and machines.
                                chunksize must be divisible by 16.

    @param      algo            AES (PyCryptodomex) of or fernet (cryptography)

    @return                     filename or bytes
    """

    in_size, in_close, in_stream, out_close, out_return, out_stream = open_input_output(
        filename, out_filename)

    encryptor, origsize, chunksize = get_encryptor(
        key, algo, out_stream=out_stream, in_size=in_size, chunksize=chunksize)

    while True:
        chunk = in_stream.read(chunksize)
        if len(chunk) == 0:
            break
        if len(chunk) % 16 != 0 and origsize is not None:
            chunk += b' ' * (16 - len(chunk) % 16)

        out_stream.write(encryptor.encrypt(chunk))

    return close_input_output(in_size, in_close, in_stream, out_close, out_return, out_stream)


def decrypt_stream(key, filename, out_filename=None, chunksize=3 * 2 ** 13, algo="AES"):
    """
    Decrypts a file using AES (CBC mode) with the given key.
    The function relies on module :epkg:`pycrypto`, :epkg:`cryptography`,
    algoritm `AES <https://fr.wikipedia.org/wiki/Advanced_Encryption_Standard>`_,
    `Fernet <http://cryptography.readthedocs.org/en/latest/fernet/>`_.

    @param      key             The encryption key - a string that must be
                                either 16, 24 or 32 bytes long. Longer keys
                                are more secure. If the data to encrypt is in bytes,
                                the key must be given in bytes too.

    @param      filename        bytes or Name of the input file
    @param      out_filename    if None, the returns bytes

    @param      chunksize       Sets the size of the chunk which the function
                                uses to read and encrypt the file. Larger chunk
                                sizes can be faster for some files and machines.
                                chunksize must be divisible by 16.

    @param      algo            AES (:epkg:`pycryptodomex`) of or fernet (cryptography)

    @return                     filename or bytes
    """
    in_size, in_close, in_stream, out_close, out_return, out_stream = open_input_output(
        filename, out_filename)

    decryptor, origsize, chunksize = get_encryptor(
        key, algo, in_stream=in_stream, chunksize=chunksize)

    while True:
        chunk = in_stream.read(chunksize)
        if len(chunk) == 0:
            break
        out_stream.write(decryptor.decrypt(chunk))
        out_stream.truncate(origsize)

    return close_input_output(in_size, in_close, in_stream, out_close, out_return, out_stream)
