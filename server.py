import socket

server_ip = '127.0.0.1'
server_port = 8888

def main():
    tcp_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    tcp_sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    tcp_sock.bind(('0.0.0.0',5555))

    udp_sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    udp_sock.bind(('0.0.0.0',5000))

    while True:
        data = udp_sock.recv(4096)
        if data[0] == 1:
            tcp_sock.send(data[1:])
            print('data transfer')
        elif data[0] == 0:
            if data[1] == 0:
                tcp_sock.connect((server_ip,server_port))
                print('connected')
            elif data[1] == 1:
                tcp_sock.close()
                tcp_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                tcp_sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
                tcp_sock.bind(('0.0.0.0',5555))
                print('disconnected')


if __name__ == "__main__":
    main()