import time

import template

class Max2769Testbench(template.TemplateTb):
    def __init__(self, dest):
        super().__init__(dest, 1030)

        self.iq_stream.send(bytes([0x0]))

    def write_reg(self, addr, val):
        assert addr == (addr & 0xF)
        assert val == (val & 0xFFFFFFF)

        data = addr | (val << 4)

        self.csr_stream.write(0x300, data)
    
    def get_samples(self):
        samples = self.iq_stream.recv()

        return samples

def main():
    tb = Max2769Testbench("10.0.0.2")

    # tb.write_reg(0x00, 0xA295011)
    # tb.write_reg(0x01, 0x8550488)
    # tb.write_reg(0x02, 0xEAFEBF2)
    # tb.write_reg(0x03, 0x9EC0008)
    # tb.write_reg(0x04, 0x0C08080)
    # tb.write_reg(0x05, 0x0000070)
    # tb.write_reg(0x06, 0x8000000)
    # tb.write_reg(0x07, 0x4004002)
    # tb.write_reg(0x02, 0xEAFEBF2)
    # tb.write_reg(0x02, 0xEAFEDF2)

    time.sleep(1)

    # print(len(tb.get_samples()))

    tb.iq_stream.send(bytes([0x1]))

if __name__ == "__main__":
    main()
