import socket
import time
import threading
from threading import Thread, Lock

# Configurações do cliente
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345
WINDOW_SIZE = 50
TIMEOUT = 1.0  # Aumentado para 1 segundo
MAX_RETRIES = 5  # Aumentado para 5 tentativas
MESSAGE_INTERVAL = 0.001

# Cria um socket UDP
udp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_client_socket.settimeout(TIMEOUT)

# Mensagens a serem enviadas
messages = [f"Mensagem {i+1}" for i in range(1000)]

# Variáveis para controle
base = 0
next_seq_num = 0
lock = Lock()
cwnd = WINDOW_SIZE
received_acks = set()

# Função para enviar mensagens com controle de fluxo e garantia de entrega
def send_with_guarantees(message, seq_num):
    global next_seq_num

    retries = 0
    while retries < MAX_RETRIES:
        udp_client_socket.sendto(f"{seq_num}:{message}".encode(), (SERVER_HOST, SERVER_PORT))
        print(f'Enviado para o servidor {SERVER_HOST}:{SERVER_PORT}: {message} (seq: {seq_num})')

        try:
            data, _ = udp_client_socket.recvfrom(1024)
            ack = int(data.decode())
            if ack == seq_num:
                with lock:
                    next_seq_num += 1
                break
        except socket.timeout:
            retries += 1
            print(f"Timeout ao aguardar confirmação para {message}. Tentativa {retries}/{MAX_RETRIES}")

        time.sleep(MESSAGE_INTERVAL)

# Função para enviar mensagens
def send_messages():
    global next_seq_num, cwnd

    threads = []
    for seq_num, message in enumerate(messages):
        while next_seq_num >= base + cwnd:
            time.sleep(MESSAGE_INTERVAL)

        thread = Thread(target=send_with_guarantees, args=(message, seq_num))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

# Função para receber confirmações
def receive_acks():
    global base, next_seq_num, cwnd, received_acks

    while base < len(messages):
        try:
            data, _ = udp_client_socket.recvfrom(1024)
            ack = int(data.decode())

            with lock:
                if ack not in received_acks:
                    received_acks.add(ack)
                    if ack >= base:
                        base = ack + 1
                        # Ajusta o tamanho da janela conforme necessário
                        cwnd = min(cwnd + 1, len(messages) - base)
        except socket.timeout:
            continue

# Inicia as threads para receber confirmações e enviar mensagens
ack_thread = Thread(target=receive_acks)
ack_thread.start()

# Envia todas as mensagens
send_messages()

# Aguarda a thread de ACKs terminar
ack_thread.join()

# Fecha o socket
udp_client_socket.close()
