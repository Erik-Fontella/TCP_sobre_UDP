import socket
def udp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('localhost', 12346))
    print("Servidor UDP aguardando dados...")


    while True:
        message, addr = server_socket.recvfrom(1024)
        print(f"Recebido '{message.decode()}' de {addr}")
        server_socket.sendto(message, addr)


if __name__ == "__main__":
    udp_server()