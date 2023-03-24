import struct
import gzip
import pickle

RECV_SIZE = 512


def pack_data(*args):
    """
    Takes multiple arguments, and returns one bytes.

    :param args: one bytes per argument
    :return: bytes where every data have length before them
    """
    out = b''
    for data in args:
        out += struct.pack("i", len(data)) + data
    return out


def unpack_data(data: bytes):
    """
    Takes bytes and split them to multiple bytes.

    :param data: one bytes with length packed before actual data
    :return: list of bytes
    """
    out = []
    index_start, index_end = 0, struct.calcsize("i")
    while index_end < len(data):
        length = struct.unpack("i", data[index_start:index_end])[0]
        index_start, index_end = index_end, index_end + length
        out.append(data[index_start:index_end])
        index_start, index_end = index_end, index_end + struct.calcsize("i")
    return out


def send_row(sock, msg):
    msg = gzip.compress(msg)
    sock.send(struct.pack("i", len(msg)) + msg)


def recv_row(sock):
    data = b""
    length_data = b""
    while len(length_data) < struct.calcsize("i"):
        length_data += sock.recv(1)
    length = struct.unpack("i", length_data)[0]

    while len(data) < length:
        if (length - len(data)) > RECV_SIZE:
            data += sock.recv(RECV_SIZE)
        else:
            data += sock.recv(length - len(data))
    data = gzip.decompress(data)
    return data
