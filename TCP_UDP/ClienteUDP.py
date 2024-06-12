import socket
import time
def udp_client(message_count, udp_times):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    for _ in range(message_count):
        start_time = time.time()
        client_socket.sendto(b"Hello, UDP Server!", ('localhost', 12346))
        client_socket.recvfrom(1024)
        end_time = time.time()
        udp_times.append(end_time - start_time)

    client_socket.close()

if __name__ == "__main__":
    udp_times = []
    message_count = 1000
    udp_client(message_count, udp_times)

    # time.sleep(1)

    # Calcular e imprimir o tempo médio de resposta
    average_time = sum(udp_times) / message_count
    print(f"Tempo médio de resposta UDP: {average_time:.6f} segundos")
