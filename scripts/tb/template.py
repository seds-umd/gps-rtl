import stream

import logging
import numpy as np
import time

class TemplateTb:
    def __init__(self, dest, source, port):
        logging.basicConfig(level=logging.INFO)

        self.stream = stream.StreamInterface(dest, source, port)

        seed = np.random.randint(2**32)
        self.rng = np.random.default_rng(seed)
        logging.info(f"Initializing RNG with seed {seed}")

    def randn(self, size):
        return self.rng.normal(1, 1, size)

    # Test function, returns score
    def test(self) -> float:
        raise NotImplementedError
    
    def run(self):
        count = 0
        total_score = 0
        last_print = time.time()

        # Gracefully exit when done
        try:
            while True:
                total_score += self.test()
                count += 1

                if time.time() - last_print > 60:
                    last_print = time.time()
                    logging.info(f"Average score: {total_score/count:0.4f}, runs: {count}")
        except KeyboardInterrupt:
            pass
