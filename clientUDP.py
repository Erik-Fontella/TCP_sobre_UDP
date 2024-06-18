import socket
import time
import threading
from threading import Thread, Lock

# Configurações do cliente
SERVER_HOST = '127.0.0.1'  # Endereço do servidor
SERVER_PORT = 12345  # Porta do servidor
WINDOW_SIZE = 50  # Tamanho da janela de congestionamento inicial
TIMEOUT = 1.0  # Tempo limite para aguardar um ACK (1 segundo)
MAX_RETRIES = 5  # Número máximo de tentativas de retransmissão
MESSAGE_INTERVAL = 0.001  # Intervalo entre envios de mensagens

# Cria um socket UDP
udp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_client_socket.settimeout(TIMEOUT)  # Define o tempo limite para o socket

# Mensagens a serem enviadas
messages = [f"Mensagem {i+1}" for i in range(1000)]  # Gera 1000 mensagens para enviar

# Variáveis para controle
base = 0  # Base da janela de congestionamento
next_seq_num = 0  # Próximo número de sequência a ser enviado
lock = Lock()  # Lock para sincronização de threads
cwnd = WINDOW_SIZE  # Janela de congestionamento inicial
received_acks = set()  # Conjunto de ACKs recebidos

# Função para enviar mensagens com controle de fluxo e garantia de entrega
def send_with_guarantees(message, seq_num):
    global next_seq_num

    retries = 0  # Contador de tentativas de envio
    while retries < MAX_RETRIES:  # Tenta enviar até o número máximo de tentativas
        udp_client_socket.sendto(f"{seq_num}:{message}".encode(), (SERVER_HOST, SERVER_PORT))  # Envia a mensagem
        print(f'Enviado para o servidor {SERVER_HOST}:{SERVER_PORT}: {message} (seq: {seq_num})')

        try:
            data, _ = udp_client_socket.recvfrom(1024)  # Aguarda um ACK
            ack = int(data.decode())  # Decodifica o ACK recebido
            if ack == seq_num:  # Verifica se o ACK corresponde ao número de sequência enviado
                with lock:
                    next_seq_num += 1  # Incrementa o próximo número de sequência a ser enviado
                break
        except socket.timeout:
            retries += 1  # Incrementa o contador de tentativas em caso de timeout
            print(f"Timeout ao aguardar confirmação para {message}. Tentativa {retries}/{MAX_RETRIES}")

        time.sleep(MESSAGE_INTERVAL)  # Aguarda um intervalo antes de tentar novamente

# Função para enviar mensagens
def send_messages():
    global next_seq_num, cwnd

    threads = []
    for seq_num, message in enumerate(messages):
        while next_seq_num >= base + cwnd:  # Aguarda até que haja espaço na janela de congestionamento
            time.sleep(MESSAGE_INTERVAL)

        thread = Thread(target=send_with_guarantees, args=(message, seq_num))  # Cria uma thread para enviar a mensagem
        thread.start()  # Inicia a thread
        threads.append(thread)

    for thread in threads:
        thread.join()  # Aguarda todas as threads terminarem

# Função para receber confirmações
def receive_acks():
    global base, next_seq_num, cwnd, received_acks

    while base < len(messages):  # Continua até que todas as mensagens sejam confirmadas
        try:
            data, _ = udp_client_socket.recvfrom(1024)  # Recebe um ACK
            ack = int(data.decode())  # Decodifica o ACK recebido

            with lock:
                if ack not in received_acks:  # Verifica se o ACK já foi recebido
                    received_acks.add(ack)  # Adiciona o ACK ao conjunto de ACKs recebidos
                    if ack >= base:
                        base = ack + 1  # Atualiza a base da janela de congestionamento
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
