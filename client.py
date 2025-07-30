import socket
import threading
import time
import random
from functions import STUN,addr2int,int2addr,wait_user_id

client_ip = '0.0.0.0'
client_port = 5555

connected = False

def handle_server_packets(udp_sock):
    global connected
    global client
    while True:
        data = udp_sock.recv(65507)
        if data[0] == 1:
            client.send(data[1:])
            print(f'server data transfer, {len(data)-1}B')
        elif data[0:2] == b'\x00\x01':
            client.close()
            connected = False
            #print('disconnected')

def main():
    global connected
    global client
    global wait
    global work

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
    tcp_sock.bind((client_ip,client_port))
    tcp_sock.listen()

    udp_sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    udp_sock.bind(('0.0.0.0',random_port))

    handler = threading.Thread(target=handle_server_packets,args=(udp_sock,))
    handler.start()
    
    while True:
        client, addr = tcp_sock.accept()
        udp_sock.sendto(b'\x00\x00',('127.0.0.1',5000)) #handle connection
        connected = True
        #print('connected')
        while True:
            if not connected:
                break
            do = True
            data = b''
            client.setblocking(False)
            while do:
                try:
                    data = client.recv(65507)
                    do = False
                except BlockingIOError:
                    pass
                except OSError:
                    do = False
            if client.fileno() != -1: 
                client.setblocking(True)
            if not data:
                udp_sock.sendto(b'\x00\x01',('127.0.0.1',5000)) #handle disconnection
                client.close()
                connected = False
                #print('disconnected')
                break
            print(f'data transfer {len(data)}B')
            udp_sock.sendto(b'\x01'+data,('127.0.0.1',5000)) #handle data

if __name__ == "__main__":
    main()