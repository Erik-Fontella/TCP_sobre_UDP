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
    
# Função do cliente UDP personalizado    
def udp_clientTop(server_address, packet_count, window_size=5, ssthresh=16):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.settimeout(1)

    def send_packet(seq_num):
        message = f"Packet {seq_num}".encode()
        udp_socket.sendto(message, server_address)
        print(f"Sent: {message.decode()}")

    def receive_ack():
        while True:
            try:
                data, _ = udp_socket.recvfrom(1024)
                ack_num = int(data.decode().split()[1])
                with lock:
                    acknowledged.add(ack_num)
                print(f"Received ACK for packet {ack_num}")
            except socket.timeout:
                break

    lock = threading.Lock()
    acknowledged = set()
    next_seq_num = 0
    congestion_window = 1
    ssthresh = 16

    def send_data():
        nonlocal next_seq_num, congestion_window
        threads = []
        while len(acknowledged) < packet_count:
            with lock:
                while next_seq_num < packet_count and len(acknowledged) + congestion_window > next_seq_num:
                    send_packet(next_seq_num)
                    next_seq_num += 1
            t = threading.Thread(target=receive_ack)
            t.start()
            threads.append(t)

            with lock:
                if congestion_window < ssthresh:
                    congestion_window *= 2
                else:
                    congestion_window += 1

            time.sleep(0.1)

        for t in threads:
            t.join()

    send_data()
    
# Função do servidor UDP personalizado
def udp_serverTop(bind_address):
    received_packets = set()
    lock = threading.Lock()
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(bind_address)

    def handle_packet(packet, addr):
        nonlocal received_packets
        seq_num = int(packet.decode().split()[1])
        with lock:
            received_packets.add(seq_num)
        print(f"Received: {packet.decode()} from {addr}")
        ack_message = f"ACK {seq_num}".encode()
        udp_socket.sendto(ack_message, addr)
        print(f"Sent: {ack_message.decode()} to {addr}")

    def start_server():
        print("UDP server is running...")
        while True:
            packet, addr = udp_socket.recvfrom(1024)
            threading.Thread(target=handle_packet, args=(packet, addr)).start()

    start_server()


# Função principal
def main():
    message_count = 1000
    tcp_times = []
    udp_times = []

    # Iniciando os servidores em threads separadas
    threading.Thread(target=tcp_server, daemon=True).start()
    threading.Thread(target=udp_server, daemon=True).start()
    threading.Thread(target=udp_serverTop, args=(('localhost', 12347),), daemon=True).start()

    # Espera para garantir que os servidores estejam prontos
    time.sleep(1)

    # Executando os clientes e medindo o tempo
    threading.Thread(target=tcp_client, args=(message_count, tcp_times)).start()
    threading.Thread(target=udp_client, args=(message_count, udp_times)).start()
    threading.Thread(target=udp_clientTop, args=(('localhost', 12347), 0), daemon=True).start()

    # Espera para garantir que os clientes terminem
    time.sleep(10)

    # Calculando tempos totais e médios
    total_tcp_time = sum(tcp_times)
    total_udp_time = sum(udp_times)
    total_udp_timeTop = sum(udp_times)
    avg_tcp_time = total_tcp_time / message_count
    avg_udp_time = total_udp_time / message_count
    avg_udp_timeTop = total_udp_timeTop / message_count

    # Plotando os gráficos
    plt.figure(figsize=(12, 6))

    # Tempo total
    plt.subplot(1, 2, 1)
    plt.bar(['TCP', 'UDP','UDP_Top'], [total_tcp_time, total_udp_time, total_udp_timeTop], color=['blue', 'orange','red'])
    plt.title('Tempo Total de Comunicação')
    plt.ylabel('Tempo (s)')

    # Tempo médio
    plt.subplot(1, 2, 2)
    plt.bar(['TCP', 'UDP','UDP_Top'], [avg_tcp_time, avg_udp_time, avg_udp_timeTop], color=['blue', 'orange','red'])
    plt.title('Tempo Médio de Comunicação')
    plt.ylabel('Tempo (s)')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()