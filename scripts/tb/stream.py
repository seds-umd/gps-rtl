import socket
import time

# Hard coded in RTL
MAX_LEN = 508


class StreamInterface:
    def __init__(self, dest, source, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((source, 0))
        self.sock.connect((dest, port))
        self.sock.settimeout(0.1)

        try:
            while len(self.sock.recv(4096)) > 0:
                pass
        except TimeoutError:
            pass

        self.rx_bytes = bytearray()
        self.rx_frames = list()

    def _send_frame(self, data: bytes, last: bool):
        packet = bytearray()
        packet.append(int(last))
        packet.extend(data)

        self.sock.send(packet)

    def send(self, data: bytes):
        for i in range(0, len(data), MAX_LEN - 1):
            self._send_frame(data[i : i + MAX_LEN - 1], len(data) - i < MAX_LEN - 1)

    def _recv_process(self):
        while True:
            try:
                data, _, _, _ = self.sock.recvmsg(4096)

                if len(data) > 0:
                    payload = data[:-1]
                    flags = data[-1]

                    self.rx_bytes.extend(payload)

                    if flags & 0b1:
                        self.rx_frames.append(self.rx_bytes)
                        self.rx_bytes = bytearray()
                        return
            except socket.timeout:
                return

    def recv(self) -> bytearray:
        self._recv_process()
        return self.rx_frames.pop(0)
