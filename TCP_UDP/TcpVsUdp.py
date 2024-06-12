## Exemplo dado pelo professor de comparação entre Tdp e Udp

import socket
import threading
import time
import matplotlib.pyplot as plt

# Função do servidor TCP
def tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 12345))
    server_socket.listen(5)
    while True:
        client_socket, _ = server_socket.accept()
        message = client_socket.recv(1024)
        client_socket.send(message)
        client_socket.close()

# Função do cliente TCP
def tcp_client(message_count, tcp_times):
    for _ in range(message_count):
        start_time = time.time()
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 12345))
        client_socket.send(b"Hello, TCP Server!")
        client_socket.recv(1024)
        client_socket.close()
        end_time = time.time()
        tcp_times.append(end_time - start_time)

# Função do servidor UDP
def udp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('localhost', 12346))
    while True:
        message, addr = server_socket.recvfrom(1024)
        server_socket.sendto(message, addr)

# Função do cliente UDP
def udp_client(message_count, udp_times):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for _ in range(message_count):
        start_time = time.time()
        client_socket.sendto(b"Hello, UDP Server!", ('localhost', 12346))
        client_socket.recvfrom(1024)
        end_time = time.time()
        udp_times.append(end_time - start_time)
    client_socket.close()

# Função principal
def main():
    message_count = 1000
    tcp_times = []
    udp_times = []

    # Iniciando os servidores em threads separadas
    threading.Thread(target=tcp_server, daemon=True).start()
    threading.Thread(target=udp_server, daemon=True).start()

    # Espera para garantir que os servidores estejam prontos
    time.sleep(1)

    # Executando os clientes e medindo o tempo
    threading.Thread(target=tcp_client, args=(message_count, tcp_times)).start()
    threading.Thread(target=udp_client, args=(message_count, udp_times)).start()

    # Espera para garantir que os clientes terminem
    time.sleep(10)

    # Calculando tempos totais e médios
    total_tcp_time = sum(tcp_times)
    total_udp_time = sum(udp_times)
    avg_tcp_time = total_tcp_time / message_count
    avg_udp_time = total_udp_time / message_count

    # Plotando os gráficos
    plt.figure(figsize=(12, 6))

    # Tempo total
    plt.subplot(1, 2, 1)
    plt.bar(['TCP', 'UDP'], [total_tcp_time, total_udp_time], color=['blue', 'orange'])
    plt.title('Tempo Total de Comunicação')
    plt.ylabel('Tempo (s)')

    # Tempo médio
    plt.subplot(1, 2, 2)
    plt.bar(['TCP', 'UDP'], [avg_tcp_time, avg_udp_time], color=['blue', 'orange'])
    plt.title('Tempo Médio de Comunicação')
    plt.ylabel('Tempo (s)')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()