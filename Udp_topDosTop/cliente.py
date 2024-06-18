import socket
import time
import threading

class UDPClient:
    def __init__(self, server_address, window_size=5):
        self.server_address = server_address  # Endereço e porta do servidor
        self.window_size = window_size  # Tamanho da janela de envio
        self.lock = threading.Lock()  # Lock para sincronização de acesso aos recursos compartilhados
        self.acknowledged = set()  # Conjunto de números de sequência reconhecidos
        self.next_seq_num = 0  # Próximo número de sequência a ser enviado
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Cria um socket UDP
        self.udp_socket.settimeout(1)  # Define o tempo limite do socket para 1 segundo
        self.congestion_window = 1  # Tamanho inicial da janela de congestionamento
        self.ssthresh = 16  # Limite da fase de slow start (limiar de congestionamento)

    def send_packet(self, seq_num):
        message = f"Packet {seq_num}".encode()  # Cria a mensagem com o número de sequência
        self.udp_socket.sendto(message, self.server_address)  # Envia a mensagem ao servidor
        print(f"Sent: {message.decode()}")  # Imprime a mensagem enviada

    def receive_ack(self):
        while True:
            try:
                data, _ = self.udp_socket.recvfrom(1024)  # Tenta receber dados do servidor
                ack_num = int(data.decode().split()[1])  # Extrai o número de sequência do ACK
                with self.lock:
                    self.acknowledged.add(ack_num)  # Adiciona o número de sequência ao conjunto de reconhecidos
                print(f"Received ACK for packet {ack_num}")  # Imprime o ACK recebido
            except socket.timeout:
                break  # Sai do loop se ocorrer um timeout

    def send_data(self, packet_count):
        threads = []  # Lista para manter as threads
        while len(self.acknowledged) < packet_count:
            with self.lock:
                # Enviar pacotes enquanto a janela de congestionamento permitir
                while (self.next_seq_num < packet_count and 
                       len(self.acknowledged) + self.congestion_window > self.next_seq_num):
                    self.send_packet(self.next_seq_num)  # Envia o pacote
                    self.next_seq_num += 1  # Incrementa o número de sequência

            t = threading.Thread(target=self.receive_ack)  # Cria uma thread para receber ACKs
            t.start()  # Inicia a thread
            threads.append(t)  # Adiciona a thread à lista
            
            # Controle de congestionamento: aumentar ou diminuir a janela de congestionamento
            with self.lock:
                if self.congestion_window < self.ssthresh:
                    self.congestion_window *= 2  # Slow start: aumenta exponencialmente
                else:
                    self.congestion_window += 1  # Congestion avoidance: aumenta linearmente
            
            time.sleep(0.1)  # Intervalo entre os envios
        
        for t in threads:
            t.join()  # Aguarda todas as threads terminarem

if __name__ == "__main__":
    client = UDPClient(('localhost', 12345))  # Cria uma instância do cliente UDP com o endereço do servidor
    client.send_data(1000)  # Envia 1000 pacotes de dados
