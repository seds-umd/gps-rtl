import time

import template


class Max2769Testbench(template.TemplateTb):
    def __init__(self, dest):
        super().__init__(dest, 1030)

        self.iq_stream.use_last = False
        self.iq_stream.send(bytes([0x0]))

    def write_reg(self, addr, val):
        assert addr == (addr & 0xF)
        assert val == (val & 0xFFFFFFF)

        data = addr | (val << 4)

        self.csr_stream.write(0x300, data)

    def write_conf1_reg(
        self,
        lnamode: int,
        anten: int,
        fcen: int,
        fbw: int,
        f3or5: int,
        fcenx: int,
        fgain: int,
        chipen: int = 1,
        idle: int = 0,
        mixpole: int = 0,
        mixen: int = 1,
    ):
        reserved = 0x229 << 16

        val = (
            ((chipen & 0x1) << 27)
            | ((idle & 0x1) << 26)
            | ((mixpole & 0x1) << 15)
            | ((lnamode & 0x3) << 13)
            | ((mixen & 0x1) << 12)
            | ((anten & 0x1) << 11)
            | ((fcen & 0x3F) << 5)
            | ((fbw & 0x3) << 3)
            | ((f3or5 & 0x1) << 2)
            | ((fcenx & 0x1) << 1)
            | ((fgain & 0x1))
            | reserved
        )

        print(f"Write conf 1: {hex(val)}")
        self.write_reg(0x00, val)

    def write_conf2_reg(
        self,
        iqen: int = 1,
        gainref: int = 170,
        agcmode: int = 0,
        format: int = 2,
        bits: int = 2,
        drvcfg: int = 0,
    ):
        reserved = 0x1 << 3

        val = (
            ((iqen & 0x1) << 27)
            | ((gainref & 0x1FF) << 15)
            | ((agcmode & 0x3) << 11)
            | ((format & 0x3) << 9)
            | ((bits & 0x7) << 6)
            | ((drvcfg & 0x3) << 4)
            | reserved
        )

        print(f"Write conf 2: {hex(val)}")
        self.write_reg(0x01, val)

    def write_conf3_reg(
        self,
        gainin: int,
        hiloaden: int,
        fhipen: int,
        pgaien: int,
        pgaqen: int,
        strmen: int,
        strmstart: int,
        strmstop: int,
        strmbits: int,
        stampen: int,
        timesyncen: int,
        datasyncen: int,
        strmrst: int,
    ):
        reserved = (0x1 << 21) | (0xF << 16) | (0x1 << 14) | (0x7 << 6)

        val = (
            ((gainin & 0x3F) << 22)
            | ((hiloaden & 0x1) << 20)
            | ((fhipen & 0x1) << 16)
            | ((pgaien & 0x1) << 13)
            | ((pgaqen & 0x1) << 12)
            | ((strmen & 0x1) << 11)
            | ((strmstart & 0x1) << 10)
            | ((strmstop & 0x1) << 9)
            | ((strmbits & 0x3) << 4)
            | ((stampen & 0x1) << 3)
            | ((timesyncen & 0x1) << 2)
            | ((datasyncen & 0x1) << 1)
            | ((strmrst & 0x1) << 0)
            | reserved
        )

        print(f"Write conf 3: {hex(val)}")
        self.write_reg(0x02, val)

    def write_clock_reg(self, l: int, m: int, fclk, adcclk, serclk, mode):
        val = (
            ((l & 0xFFF) << 16)
            | ((m & 0xFFF) << 4)
            | ((fclk & 0x1) << 3)
            | ((adcclk & 0x1) << 2)
            | ((serclk & 0x1) << 1)
            | (mode & 0x1)
        )
        print(f"Write clock reg: {hex(val)}")
        self.write_reg(0x07, val)

    def get_samples(self):
        samples = self.iq_stream.recv()

        # Decode bytes
        samples = [
            int.from_bytes(samples[i : i + 2], "little")
            for i in range(0, len(samples), 2)
        ]

        # Split into timestamp and sample
        samples = [(x >> 4, x & 0xF) for x in samples]

        return samples


def main():
    tb = Max2769Testbench("10.0.0.2")

    tb.write_conf1_reg(
        chipen=1,
        lnamode=2,
        anten=0,
        fcen=0,
        fbw=0,
        f3or5=0,
        fcenx=0,
        fgain=1,
    )
    tb.write_conf2_reg()
    tb.write_conf3_reg(
        gainin=58,
        hiloaden=0,
        fhipen=1,
        pgaien=1,
        pgaqen=1,
        strmen=0,
        strmstart=0,
        strmstop=1,
        strmbits=3,
        stampen=0,
        timesyncen=0,
        datasyncen=1,
        strmrst=0,
    )
    tb.write_reg(0x03, 0x9EC0008)
    tb.write_reg(0x04, 0x0C08080)
    tb.write_reg(0x05, 0x0000070)
    tb.write_reg(0x06, 0x8000000)
    tb.write_clock_reg(l=1024, m=1024, fclk=1, adcclk=0, serclk=0, mode=1)
    tb.write_conf3_reg(
        gainin=58,
        hiloaden=0,
        fhipen=1,
        pgaien=1,
        pgaqen=1,
        strmen=1,
        strmstart=1,
        strmstop=0,
        strmbits=3,
        stampen=0,
        timesyncen=0,
        datasyncen=1,
        strmrst=0,
    )

    time.sleep(1)

    samples = []

    while True:
        try:
            samples.extend(tb.get_samples())
        except:
            break

    print(len(samples))

    tb.iq_stream.send(bytes([0x1]))


if __name__ == "__main__":
    main()
