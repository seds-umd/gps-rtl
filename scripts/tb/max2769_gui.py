from imgui_bundle import imgui, immapp, implot
import numpy as np
from test_max2769 import Max2769Testbench, setup_regs_default, normalize_iq
import queue
import time
import threading
import atexit

class Gui:
    def __init__(self):
        self.log_text = []

        self.tb = Max2769Testbench("192.168.200.2")
        self.tb.set_direct_acquisition(False)
        setup_regs_default(self.tb)

        self.sample_thread = threading.Thread(target=self._sample_runner, daemon=True)
        self.results_thread = threading.Thread(target=self._acquisition_runner, daemon=True)

        self.sample_thread.start()
        self.results_thread.start()

        self.snrs = np.zeros(32)

        atexit.register(self.cleanup)

    # Get samples, send to acquisition
    def _sample_runner(self):
        self.tb.set_enable(True)

        while True:
            time.sleep(0)

            samples = []

            # print("samples", len(self.tb.iq_stream.rx_frames))
            while len(self.tb.iq_stream.rx_frames) > 0 and len(samples) < 500:
                incoming = self.tb.iq_stream.recv()
                incoming = np.array(incoming, dtype=np.uint8)

                first = incoming & 0xF
                second = incoming >> 4

                incoming = np.empty(len(incoming)*2, dtype=np.uint8)
                incoming[::2] = first
                incoming[1::2] = second

                samples.append(incoming)

            if len(samples) > 0:
                samples = np.concatenate(samples)
                samples = normalize_iq(samples)
                # print(f"Sending {len(samples)} samples")
                self.tb.acq_results.send_samples(samples, threaded=False)

            # Clear buffer if it gets too big
            l = len(self.tb.iq_stream.rx_frames)
            if l > 1000:
                self.tb.iq_stream.rx_frames = self.tb.iq_stream.rx_frames[l-1000:]

    def _acquisition_runner(self):
        while True:
            time.sleep(0)

            while len(self.tb.acq_results.rx_frames) > 0:
                res = self.tb.get_results()
                # print("got result", res)

                self.log_text.append(f"{res}\n")

                while len(self.log_text) > 200:
                    self.log_text.pop(0)

                self.snrs[res["sv"]-1] = res["snr"]

    def debug_output(self):
        if imgui.begin_child("text_region"):
            for line in self.log_text:
                imgui.text_unformatted(line)

            imgui.set_scroll_here_y(1.0)

            imgui.end_child()

    def snr_graph(self):
        if implot.begin_plot("SNR", flags=implot.Flags_.no_legend):
            implot.setup_axes("Satellite Number", "")
            implot.setup_axes_limits(0, 33, 0, 30)
            implot.plot_bars("SNR", self.snrs, bar_size=0.5, shift=1, offset=1)
            implot.end_plot()

    def run(self):
        imgui.set_next_window_pos(imgui.ImVec2(0, 0))
        imgui.set_next_window_size(imgui.get_io().display_size)
        imgui.begin("GPS Demo", flags=imgui.WindowFlags_.no_title_bar | imgui.WindowFlags_.no_resize)

        if imgui.begin_table("layout", 2):
            imgui.table_next_column()
            self.snr_graph()

            imgui.table_next_column()
            self.debug_output()

            imgui.end_table()

        imgui.end()

    def cleanup(self):
        print("Turning off samples")
        print(f"Incoming sample buffer: {len(self.tb.iq_stream.rx_frames)}")
        self.tb.set_enable(False)

if __name__ == "__main__":
    gui = Gui()

    immapp.run(
        gui_function=gui.run,
        window_title="GPS Demo",
        fps_idle=60,
        with_implot=True,
    )
