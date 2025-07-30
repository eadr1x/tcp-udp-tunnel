import socket
import threading
import time

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

    tcp_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    tcp_sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    tcp_sock.bind((client_ip,client_port))
    tcp_sock.listen()

    udp_sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    udp_sock.bind(('0.0.0.0',5001))

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