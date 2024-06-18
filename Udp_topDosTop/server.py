import socket
import threading

class UDPServer:
    def __init__(self, bind_address):
        self.bind_address = bind_address  # Endereço e porta para ligar o servidor
        self.received_packets = set()  # Conjunto para armazenar números de sequência de pacotes recebidos
        self.lock = threading.Lock()  # Lock para sincronização de acesso ao conjunto
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Cria um socket UDP
        self.udp_socket.bind(self.bind_address)  # Liga o socket ao endereço e porta especificados

    def handle_packet(self, packet, addr):
        seq_num = int(packet.decode().split()[1])  # Extrai o número de sequência do pacote recebido
        with self.lock:
            self.received_packets.add(seq_num)  # Adiciona o número de sequência ao conjunto de pacotes recebidos
        print(f"Received: {packet.decode()} from {addr}")  # Exibe a mensagem recebida
        ack_message = f"ACK {seq_num}".encode()  # Cria uma mensagem de ACK com o número de sequência
        self.udp_socket.sendto(ack_message, addr)  # Envia o ACK de volta para o cliente
        print(f"Sent: {ack_message.decode()} to {addr}")  # Exibe a mensagem de ACK enviada

    def start(self):
        print("UDP server is running...")  # Indica que o servidor está em execução
        while True:
            packet, addr = self.udp_socket.recvfrom(1024)  # Recebe um pacote do cliente
            # Cria uma nova thread para lidar com o pacote recebido
            threading.Thread(target=self.handle_packet, args=(packet, addr)).start()

if __name__ == "__main__":
    server = UDPServer(('localhost', 12345))  # Cria uma instância do servidor UDP
    server.start()  # Inicia o servidor
