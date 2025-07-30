import socket
import threading

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

    tcp_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    tcp_sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    tcp_sock.bind(('0.0.0.0',5555))

    udp_sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    udp_sock.bind(('0.0.0.0',5000))

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
                tcp_sock.bind(('0.0.0.0',5555))
                connected = False
                #print('disconnected')


if __name__ == "__main__":
    main()