from pulsestreamer import PulseStreamer, Sequence, ClockSource


class PulseStreamerDriver:

    def __init__(self, ip: str, clock: str = "internal"):
        self.ip       = ip
        self.clock   = clock  # "internal" ou "external"
        self._device  = None

    def connect(self):
        try:
            self._device = PulseStreamer(self.ip)
            if self.clock == "external":
                self.select_external_clock()
            else:
                self.select_internal_clock()
            print(f"PulseStreamer connected at {self.ip} — clock: {self.clock}")
        except Exception as e:
            print(f"[Connection error] {e}")
            self._device = None

    def disconnect(self):
        if self._device:
            self._device.reset()
            self._device = None

    def is_connected(self) -> bool:
        return self._device is not None

    def select_internal_clock(self):
        self._device.selectClock(ClockSource.INTERNAL)

    def select_external_clock(self):
        self._device.selectClock(ClockSource.EXT_10MHZ)

    def create_sequence(self) -> Sequence:
        return self._device.createSequence()

    def load_sequence(self, sequence: Sequence):
        self._sequence = sequence

    def stream_infinite(self, sequence: Sequence):
        self._device.stream(sequence, PulseStreamer.REPEAT_INFINITELY)

    def stream_n_times(self, sequence: Sequence, n: int):
        self._device.stream(sequence, n)

    def stop(self):
        try:
            self._device.constant()
        except Exception as e:
            print(f"[PulseStreamer] stop failed: {e}")
            self._device = None

    def reset(self):
        try:
            self._device.reset()
        except Exception as e:
            print(f"[PulseStreamer] reset failed: {e}")
            self._device = None
