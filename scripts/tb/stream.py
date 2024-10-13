import random
import socket
import time

# Hard coded in RTL
MAX_LEN = 508


class StreamInterface:
    def __init__(self, dest, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.connect((dest, port))
        self.sock.settimeout(0.1)

        try:
            while len(self.sock.recv(4096)) > 0:
                pass
        except (TimeoutError, socket.timeout):
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


class AxilInterface:
    def __init__(self, dest, port):
        self.stream = StreamInterface(dest, port)

        self._command_id = random.randint(0, 2**16 - 1)
        self._reads = {}

    def write(self, addr: int, data: int):
        pkt = bytearray()
        pkt.append(0x80)
        pkt.extend(self._command_id.to_bytes(2, "little"))
        pkt.extend(addr.to_bytes(4, "little"))
        pkt.extend(data.to_bytes(4, "little"))

        self._command_id += 1
        self._command_id &= 0xFFFF

        self.stream.send(pkt)

    def _do_recv(self):
        try:
            while True:
                pkt = self.stream.recv()

                id = int.from_bytes(pkt.payload[:2], "little")
                value = int.from_bytes(pkt.payload[2:], "little")

                self._reads[id] = value
        except IndexError:
            pass

    def read(self, addr: int) -> int:
        pkt = bytearray()
        pkt.append(0x00)
        pkt.extend(self._command_id.to_bytes(2, "little"))
        pkt.extend(addr.to_bytes(4, "little"))

        sent_id = self._command_id

        self._command_id += 1
        self._command_id &= 0xFFFF

        self.stream.send(pkt)
        self._do_recv()

        return self._reads.pop(sent_id)
