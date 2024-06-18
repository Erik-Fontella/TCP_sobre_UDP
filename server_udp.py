import socket
import heapq
import threading
from threading import Lock

# Configurações do servidor
SERVER_HOST = '127.0.0.1'  # Endereço do servidor
SERVER_PORT = 12345  # Porta do servidor

# Cria um socket UDP
udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Liga o socket ao endereço e porta
udp_server_socket.bind((SERVER_HOST, SERVER_PORT))

print(f"Servidor UDP está ouvindo em {SERVER_HOST}:{SERVER_PORT}...")

# Estrutura para armazenar mensagens recebidas fora de ordem
received_messages = []  # Heap para armazenar mensagens fora de ordem
heap_lock = Lock()  # Lock para sincronização de acesso ao heap
expected_seq_num = 0  # Número de sequência esperado
acknowledged = set()  # Conjunto de números de sequência já reconhecidos

# Função para processar mensagens fora de ordem
def process_messages():
    global received_messages, expected_seq_num
    while True:
        with heap_lock:
            # Processa mensagens na ordem correta
            while received_messages and received_messages[0][0] == expected_seq_num:
                _, message = heapq.heappop(received_messages)  # Remove a mensagem da heap
                print(f"Mensagem recebida e processada: {message}")
                expected_seq_num += 1  # Incrementa o número de sequência esperado

# Inicia a thread para processamento de mensagens
process_thread = threading.Thread(target=process_messages)
process_thread.start()

# Loop principal para receber mensagens
while True:
    try:
        data, client_address = udp_server_socket.recvfrom(1024)  # Recebe dados do cliente
        seq_num, message = data.decode().split(":", 1)  # Decodifica a mensagem recebida
        seq_num = int(seq_num)  # Converte o número de sequência para inteiro

        with heap_lock:
            if seq_num not in acknowledged:  # Verifica se o número de sequência já foi reconhecido
                heapq.heappush(received_messages, (seq_num, message))  # Adiciona a mensagem à heap
                acknowledged.add(seq_num)  # Adiciona o número de sequência ao conjunto de reconhecidos
                # Envia uma confirmação (ACK) de volta para o cliente
                udp_server_socket.sendto(str(seq_num).encode(), client_address)
                print(f"Enviado ACK para {client_address}: {seq_num}")
    except ConnectionResetError:
        print("Aviso: Conexão forçada foi cancelada pelo cliente.")
        continue

# Fecha o socket do servidor (isso nunca é alcançado no código acima)
udp_server_socket.close()
