"""Exercise host framing over real loopback UDP, without an FPGA."""
import importlib.util
from pathlib import Path
import socket
import time
import unittest

spec = importlib.util.spec_from_file_location("gps_udp_stream", Path(__file__).parents[1] / "tb" / "stream.py")
stream = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stream)


class UdpClientTests(unittest.TestCase):
    def setUp(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind(("127.0.0.1", 0))
        self.server.settimeout(0.5)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.connect(self.server.getsockname())
        self.addCleanup(self.server.close)
        self.addCleanup(self.client_socket.close)

    def test_last_fragment_at_packet_boundary(self):
        client = stream.StreamInterface.__new__(stream.StreamInterface)
        client.sock = self.client_socket
        for size in [1, 506, 507, 508, 1014, 1015]:
            with self.subTest(size=size):
                data = bytes(i % 256 for i in range(size))
                client.send(data)
                packets = [self.server.recv(4096) for _ in range((size + 506) // 507)]
                self.assertEqual(b"".join(p[1:] for p in packets), data)
                self.assertEqual([p[0] for p in packets], [0] * (len(packets) - 1) + [1])

    def test_read_without_reply_has_bounded_timeout(self):
        client = stream.AxilInterface.__new__(stream.AxilInterface)
        client.sock = self.client_socket
        client._command_id = 0xFFFF
        client._reads = {}
        start = time.monotonic()
        with self.assertRaisesRegex(TimeoutError, "0x00000004"):
            client.read(0x04, timeout=0.02)
        self.assertLess(time.monotonic() - start, 0.5)
        self.assertEqual(self.server.recv(4096), b"\x01\x00\xff\xff\x04\x00\x00\x00")
        self.assertEqual(client._command_id, 0)


if __name__ == "__main__":
    unittest.main()
