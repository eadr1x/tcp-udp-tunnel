import socket

client_ip = '0.0.0.0'
client_port = 5555

def main():
    tcp_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    tcp_sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    tcp_sock.bind((client_ip,client_port))
    tcp_sock.listen()

    udp_sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    udp_sock.bind(('0.0.0.0',5001))

    while True:
        client, addr = tcp_sock.accept()
        udp_sock.sendto(b'\x00\x00',('127.0.0.1',5000)) #handle connection
        print('connected')
        while True:
            data = client.recv(4096)
            if not data:
                udp_sock.sendto(b'\x00\x01',('127.0.0.1',5000)) #handle disconnection
                client.close()
                print('disconnected')
                break
            print('data transfer')
            udp_sock.sendto(b'\x01'+data,('127.0.0.1',5000)) #handle data
if __name__ == "__main__":
    main()