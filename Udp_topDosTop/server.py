import socket
import threading

class UDPServer:
    def __init__(self, bind_address):
        self.bind_address = bind_address
        self.received_packets = set()
        self.lock = threading.Lock()
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind(self.bind_address)

    def handle_packet(self, packet, addr):
        seq_num = int(packet.decode().split()[1])
        with self.lock:
            self.received_packets.add(seq_num)
        print(f"Received: {packet.decode()} from {addr}")
        ack_message = f"ACK {seq_num}".encode()
        self.udp_socket.sendto(ack_message, addr)
        print(f"Sent: {ack_message.decode()} to {addr}")

    def start(self):
        print("UDP server is running...")
        while True:
            packet, addr = self.udp_socket.recvfrom(1024)
            threading.Thread(target=self.handle_packet, args=(packet, addr)).start()

if __name__ == "__main__":
    server = UDPServer(('localhost', 12345))
    server.start()  
