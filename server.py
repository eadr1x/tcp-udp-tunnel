import socket
import threading
import time
import random
from functions import STUN,addr2int,int2addr,wait_user_id

server_ip = '127.0.0.1'
server_port = 25565

connected = False

def handle_server_packets(udp_sock):
    global tcp_sock
    global connected
    while True:
        if connected:
            data = b''
            try:
                data = tcp_sock.recv(65507)
            except ConnectionAbortedError:
                pass
            except OSError:
                pass
            if not data:
                tcp_sock.close()
                tcp_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                tcp_sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
                tcp_sock.bind(('0.0.0.0',5555))
                udp_sock.sendto(b'\x00\x01',('127.0.0.1',5001))
                connected = False
            else:
                udp_sock.sendto(b'\x01' + data, ('127.0.0.1',5001))
                print(f'server data transfer {len(data)}B')

def main():
    global connected
    global tcp_sock

    random_port = random.randint(20000, 30000)
    public_ip, public_port = STUN(random_port)
    user_id = addr2int(public_ip, public_port)
    print("User ID:", user_id)

    wait = True
    user_wait = threading.Thread(target=wait_user_id,args=(random_port,),daemon=True)
    user_wait.start()

    remote_id = 0
    while True:
        try:
            remote_id = int(input("Enter remote ID: "))
        except ValueError:
            print("Invalid ID, try again")
        if remote_id:
            wait = False
            break

    remote_ip,remote_port = int2addr(remote_id)
    print("The remote is :",remote_ip,remote_port)
    work = True

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", random_port))
    sock.setblocking(False)

    while work:
        sock.sendto(b"\x01\x00", (remote_ip,remote_port))
        try:
            ans, addr = sock.recvfrom(2048)
            work = False
            break
        except:
            time.sleep(0.01)

    for i in range(20):
        sock.sendto(b"\x01\x00", (remote_ip, remote_port))
        time.sleep(0.1)

    sock.close()
    print("Connected!")


    tcp_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    tcp_sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    #tcp_sock.bind(('0.0.0.0',5555))

    udp_sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    udp_sock.bind(('0.0.0.0',random_port))

    handler = threading.Thread(target=handle_server_packets,args=(udp_sock,))
    handler.start()

    while True:
        data = udp_sock.recv(65507)
        if data[0] == 1:
            tcp_sock.send(data[1:])
            print(f'data transfer {len(data)}B')
        elif data[0] == 0:
            if data[1] == 0:
                tcp_sock.connect((server_ip,server_port))
                connected = True
                #print('connected')
            elif data[1] == 1:
                tcp_sock.close()
                tcp_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                tcp_sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
                #tcp_sock.bind(('0.0.0.0',5555))
                connected = False
                #print('disconnected')


if __name__ == "__main__":
    main()