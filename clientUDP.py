import socket
import threading
import time

# Configurações do cliente
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345
WINDOW_SIZE = 50
TIMEOUT = 5.0  # Aumentado para 5 segundos
MAX_RETRIES = 5  # Número máximo de tentativas
MESSAGE_INTERVAL = 0.1  # Intervalo entre as mensagens

# Cria um socket UDP
udp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_client_socket.settimeout(TIMEOUT)

# Mensagens a serem enviadas
messages = [f"Mensagem {i+1}" for i in range(100)]

# Variáveis para controle
base = 0
next_seq_num = 0
lock = threading.Lock()
received_acks = set()

# Função para enviar mensagens com controle de fluxo e garantia de entrega
def send_with_guarantees(message, seq_num):
    retries = 0
    while retries < MAX_RETRIES:
        if seq_num < base:
            print(f"IGNORANDO reenvio de mensagem {seq_num} que já foi confirmada.")
            return
        
        udp_client_socket.sendto(f"{seq_num}:{message}".encode(), (SERVER_HOST, SERVER_PORT))
        print(f'Enviado para o servidor {SERVER_HOST}:{SERVER_PORT}: {message} (seq: {seq_num})')

        try:
            data, _ = udp_client_socket.recvfrom(1024)
            ack = int(data.decode())
            
            with lock:
                received_acks.add(ack)
                while base in received_acks:
                    base += 1
            print(f"Recebido ACK {ack} para mensagem {seq_num}")
            return
        
        except socket.timeout:
            retries += 1
            print(f"Timeout ao aguardar confirmação para {message}. Tentativa {retries}/{MAX_RETRIES}")
            time.sleep(2**retries)  # Backoff exponencial

    print(f"Não foi possível confirmar {message} após {MAX_RETRIES} tentativas.")

# Função para enviar mensagens
def send_messages():
    global next_seq_num

    threads = []
    for seq_num, message in enumerate(messages):
        while True:
            with lock:
                if next_seq_num < base + WINDOW_SIZE:
                    next_seq_num += 1
                    break

            time.sleep(MESSAGE_INTERVAL)

        thread = threading.Thread(target=send_with_guarantees, args=(message, seq_num))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

# Inicia as threads para enviar mensagens
send_messages()

# Fecha o socket do cliente
udp_client_socket.close()
