import template

import numpy as np
import time
import logging

import gps.rust


class AcquisitionTestbench(template.IqTestbench):
    def get_availability(self) -> int:
        return self.csr_stream.read(0x10)

    def get_results(self):
        res_bytes = self.iq_stream.recv()
        res_bytes.reverse()

        res_int = 0
        res = {}

        for i in range(len(res_bytes)):
            res_int |= res_bytes[i]
            res_int <<= 8

        # Discard padding byte
        res_int >>= 8

        # Order is opposite of
        res["sv"] = res_int & 0x3F
        res_int >>= 6

        res["freq"] = res_int & 0xFFF
        res_int >>= 12

        if res["freq"] > 2**11:
            res["freq"] = res["freq"] - 2**12

        res["phase"] = res_int & 0xFFF
        res_int >>= 12

        res["snr"] = res_int & 0xFF
        res_int >>= 8

        return res

    def get_all_results(self):
        results = []

        while True:
            try:
                res = self.get_results()

                results.append(res)
            except IndexError:
                break

        return results

    # Score is the fraction of visible SVs that were detected minus fraction of false detections
    def test(self, dur=60, threshold=10) -> float:
        start = time.time()

        self.reset()
        configs = gps.rust.sim.random_config(8, 2, 5e3)
        svs = [c.sv for c in configs]
        svs.sort()
        samples = gps.rust.sim.generate_signal(
            template.FS, int(template.FS * dur), configs
        )
        self.send_samples(samples, False)

        time.sleep(0.5)
        input_count = self.csr_stream.read(0x04)

        if input_count != len(samples):
            self.log.warning(f"Sent {len(samples)} samples, got {input_count}")

        detections = {i: 0 for i in range(1, 33)}
        results = self.get_all_results()

        for res in results:
            if res["snr"] > threshold:
                detections[res["sv"]] += 1

        detected_svs = [key for key, value in detections.items() if value > 0]

        score = 0

        for sv in detected_svs:
            if sv in svs:
                score += 1
            else:
                score -= 1

        score /= len(svs)
        total = sum(detections.values())
        unique = sum([1 for x in detections.values() if x > 0])

        end = time.time()

        logging.info(
            f"Test took {end-start:.2f}s, got {total} detections ({unique} unique), score={score}"
        )

        return score

    def run(self):
        count = 0
        total_score = 0

        # Gracefully exit when done
        try:
            while True:
                total_score += self.test()
                count += 1

                logging.info(f"Average score: {total_score/count:0.4f}, runs: {count}")
        except KeyboardInterrupt:
            pass


def file_data_test():
    tb = AcquisitionTestbench("10.0.0.2")

    threshold = 10

    for i in range(10):
        tb.reset()

        file = f"../../../gps-model/data/test{i}.ci16"
        tb.send_file(file, np.int8)

        print(f"Sending sample data {i} - {len(tb.samples_quant)} samples")
        time.sleep(0.5)
        input_count = tb.csr_stream.read(0x04)

        assert input_count == len(
            tb.samples_quant
        ), f"Sent {len(tb.samples_quant)} samples, got {input_count}"

        detections = {i: 0 for i in range(1, 33)}

        results = []

        while True:
            try:
                res = tb.get_results()

                results.append(res)
            except IndexError:
                break

        for res in results:
            if res["snr"] > threshold:
                detections[res["sv"]] += 1

        total = sum(detections.values())
        unique = sum([1 for x in detections.values() if x > 0])

        print(f"Got {total} detections, {unique} unqiue SVs")
        print("")


def infinite_test():
    tb = AcquisitionTestbench("10.0.0.2")
    tb.run()


if __name__ == "__main__":
    # file_data_test()
    infinite_test()
