"""Gravação do microfone com sounddevice, direto na memória."""

import numpy as np
import sounddevice as sd

SAMPLE_RATE = 16000  # o Whisper trabalha com 16 kHz


class Recorder:
    """Grava o microfone entre start() e stop()."""

    def __init__(self, device=None, rate=SAMPLE_RATE):
        self.device = device  # None = microfone padrão do sistema
        self.rate = rate
        self._chunks = []
        self._stream = None

    def _callback(self, indata, frames, time, status):
        # O PortAudio chama esta função (numa thread dele) a cada pedaço de
        # áudio gravado. Guardamos uma cópia, porque o buffer é reaproveitado.
        self._chunks.append(indata.copy())

    def start(self):
        self._chunks = []
        self._stream = sd.InputStream(
            samplerate=self.rate,
            channels=1,
            dtype="float32",
            device=self.device,
            callback=self._callback,
        )
        self._stream.start()

    def stop(self):
        """Para a gravação e devolve o áudio como um array float32 (mono)."""
        self._stream.stop()
        self._stream.close()
        self._stream = None
        if not self._chunks:
            return np.zeros(0, dtype=np.float32)
        # Cada pedaço tem formato (amostras, 1 canal); juntamos e tiramos o canal
        return np.concatenate(self._chunks)[:, 0]
