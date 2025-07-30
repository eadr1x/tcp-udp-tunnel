import socket
import time

wait = False

def addr2int(ip, port: int):
    binport = bin(port)[2:].rjust(16, "0")
    binip = "".join([bin(int(i))[2:].rjust(8, "0") for i in ip.split(".")])
    return int(binip + binport, 2)


def int2addr(num):
    num = bin(num)[2:].rjust(48, "0")
    num = [str(int(i, 2)) for i in [num[0:8], num[8:16], num[16:24], num[24:32], num[32:48]]]
    return ".".join(num[0:4]), int(num[4])


def STUN(port, host="stun.ekiga.net"):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", port))
    sock.setblocking(False)
    server = socket.gethostbyname(host)
    work = True
    while work:
        sock.sendto(b"\x00\x01\x00\x00!\x12\xa4B\xd6\x85y\xb8\x11\x030\x06xi\xdfB", (server, 3478),)
        for i in range(20):
            try:
                ans, addr = sock.recvfrom(2048)
                work = False
                break
            except:
                time.sleep(0.01)
    sock.close()
    return socket.inet_ntoa(ans[28:32]), int.from_bytes(ans[26:28], byteorder="big")

def wait_user_id(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", port))
    while wait:
        sock.sendto(b'\x01\x00',('123.45.67.89',12345))
        time.sleep(1)
    sock.close()