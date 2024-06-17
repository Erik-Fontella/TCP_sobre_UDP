import socket
import heapq
import threading
from threading import Lock

# Configurações do servidor
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345

# Cria um socket UDP
udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Liga o socket ao endereço e porta
udp_server_socket.bind((SERVER_HOST, SERVER_PORT))

print(f"Servidor UDP está ouvindo em {SERVER_HOST}:{SERVER_PORT}...")

# Estrutura para armazenar mensagens recebidas fora de ordem
received_messages = []
heap_lock = Lock()
expected_seq_num = 0
acknowledged = set()

# Função para processar mensagens fora de ordem
def process_messages():
    global received_messages, expected_seq_num
    while True:
        with heap_lock:
            while received_messages and received_messages[0][0] == expected_seq_num:
                _, message = heapq.heappop(received_messages)
                print(f"Mensagem recebida e processada: {message}")
                expected_seq_num += 1

# Inicia a thread para processamento de mensagens
process_thread = threading.Thread(target=process_messages)
process_thread.start()

# Loop principal para receber mensagens
while True:
    try:
        data, client_address = udp_server_socket.recvfrom(1024)
        seq_num, message = data.decode().split(":", 1)
        seq_num = int(seq_num)

        with heap_lock:
            if seq_num not in acknowledged:
                heapq.heappush(received_messages, (seq_num, message))
                acknowledged.add(seq_num)
                # Envia uma confirmação (ACK) de volta para o cliente
                udp_server_socket.sendto(str(seq_num).encode(), client_address)
                print(f"Enviado ACK para {client_address}: {seq_num}")
    except ConnectionResetError:
        print("Aviso: Conexão forçada foi cancelada pelo cliente.")
        continue

# Fecha o socket do servidor (isso nunca é alcançado no código acima)
udp_server_socket.close()
