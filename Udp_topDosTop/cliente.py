import socket
import time
import threading

class UDPClient:
    def __init__(self, server_address, window_size=5):
        self.server_address = server_address
        self.window_size = window_size
        self.lock = threading.Lock()
        self.acknowledged = set()
        self.next_seq_num = 0
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.settimeout(1)
        self.congestion_window = 1  # Congestion window size starts with 1
        self.ssthresh = 16  # Slow start threshold

    def send_packet(self, seq_num):
        message = f"Packet {seq_num}".encode()
        self.udp_socket.sendto(message, self.server_address)
        print(f"Sent: {message.decode()}")

    def receive_ack(self):
        while True:
            try:
                data, _ = self.udp_socket.recvfrom(1024)
                ack_num = int(data.decode().split()[1])
                with self.lock:
                    self.acknowledged.add(ack_num)
                print(f"Received ACK for packet {ack_num}")
            except socket.timeout:
                break

    def send_data(self, packet_count):
        threads = []
        while len(self.acknowledged) < packet_count:
            with self.lock:
                # Enviar pacotes enquanto a janela de congestionamento permitir
                while (self.next_seq_num < packet_count and 
                       len(self.acknowledged) + self.congestion_window > self.next_seq_num):
                    self.send_packet(self.next_seq_num)
                    self.next_seq_num += 1

            t = threading.Thread(target=self.receive_ack)
            t.start()
            threads.append(t)
            
            # Controle de congestionamento: aumentar ou diminuir a janela de congestionamento
            with self.lock:
                if self.congestion_window < self.ssthresh:
                    self.congestion_window *= 2  # Slow start
                else:
                    self.congestion_window += 1  # Congestion avoidance
            
            time.sleep(0.1)  # Simulate sending interval
        
        for t in threads:
            t.join()

if __name__ == "__main__":
    client = UDPClient(('localhost', 12345))
    client.send_data(1000)
