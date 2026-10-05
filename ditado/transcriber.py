"""Transcrição com faster-whisper. O modelo é carregado uma vez só."""

from faster_whisper import WhisperModel


class Transcriber:
    def __init__(self, model="small", language="pt"):
        # Por enquanto só CPU com int8 (rápido e leve). A GPU (CUDA) fica para a fase 5.
        # Na primeira vez, o modelo é baixado da internet e guardado em ~/.cache/huggingface.
        self.model = WhisperModel(model, device="cpu", compute_type="int8")
        self.language = language

    def transcribe(self, audio):
        """Recebe o áudio como um array float32 de 16 kHz, mono."""
        segments, _info = self.model.transcribe(
            audio,
            language=self.language,
            vad_filter=True,  # corta os trechos de silêncio
            beam_size=5,
        )
        # segments é um gerador: a transcrição de verdade acontece ao percorrê-lo
        return " ".join(segment.text.strip() for segment in segments).strip()
