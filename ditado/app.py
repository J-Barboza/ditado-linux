"""Junta tudo: tecla → gravação → transcrição → colagem.

Máquina de estados:
    PARADO --(apertou)--> GRAVANDO --(soltou)--> TRANSCREVENDO --> COLANDO --> PARADO

Privacidade: as mensagens mostram só o estado, nunca o texto transcrito.
"""

import threading

from evdev import ecodes

from ditado.audio import SAMPLE_RATE, Recorder
from ditado.hotkey import listen
from ditado.notify import Notifier
from ditado.output import Paster, parse_keys
from ditado.transcriber import Transcriber

IDLE = "PARADO"
RECORDING = "GRAVANDO"
TRANSCRIBING = "TRANSCREVENDO"
PASTING = "COLANDO"

MIN_SECONDS = 0.3  # gravações menores que isso são toque acidental na tecla


class App:
    def __init__(self, config):
        self.config = config
        key_name = config["atalho"]["tecla"]
        if key_name not in ecodes.ecodes:
            raise ValueError(f"Tecla desconhecida em atalho.tecla: {key_name}")
        self.key = ecodes.ecodes[key_name]  # ex.: "KEY_PAUSE" -> 119

        print("Carregando o modelo...")
        # Carregado uma vez só, fica na memória
        self.transcriber = Transcriber(config["whisper"]["modelo"], config["whisper"]["idioma"])
        self.paster = Paster(
            parse_keys(config["saida"]["colar_com"]), config["saida"]["restaurar_clipboard"]
        )
        self.recorder = Recorder(device=config["audio"]["dispositivo"] or None)
        self.notifier = Notifier(config["avisos"]["notificacao"], config["avisos"]["bip"])
        self.state = IDLE

    def _tell(self, message):
        """Mostra a mensagem no terminal (ou no journal) e como notificação."""
        print(message)
        self.notifier.notify(message)

    def run(self):
        print("Pronto! Segure a tecla de atalho para falar (Ctrl+C para sair).")
        # listen() fica em loop e chama on_press/on_release nesta mesma thread
        listen(on_press=self.on_press, on_release=self.on_release, key=self.key)

    def on_press(self):
        if self.state != IDLE:
            return  # ainda transcrevendo o ditado anterior: ignora
        try:
            self.recorder.start()
        except Exception as error:
            self._tell(f"Erro ao abrir o microfone: {error}")
            return
        self.state = RECORDING
        self.notifier.beep(880)
        self._tell("Gravando…")

    def on_release(self):
        if self.state != RECORDING:
            return
        self.state = TRANSCRIBING
        try:
            audio = self.recorder.stop()
        except Exception as error:
            self._tell(f"Erro ao parar a gravação: {error}")
            self.state = IDLE
            return
        self.notifier.beep(440)
        # A transcrição demora; numa thread separada ela não trava a leitura da tecla.
        # Enquanto isso o estado fica TRANSCREVENDO, e on_press() ignora a tecla.
        threading.Thread(target=self._transcribe_and_paste, args=(audio,), daemon=True).start()

    def _transcribe_and_paste(self, audio):
        try:
            if audio.size < MIN_SECONDS * SAMPLE_RATE:
                print("Gravação muito curta, ignorada.")
                return
            self._tell("Transcrevendo…")
            text = self.transcriber.transcribe(audio)
            if not text:
                self._tell("Nada reconhecido.")
                return
            self.state = PASTING
            # O espaço no fim evita que dois ditados seguidos fiquem grudados
            if self.config["saida"]["espaco_no_final"]:
                text += " "
            self.paster.paste(text)
            print("Colado.")
        except Exception as error:
            # Qualquer erro: avisa e volta para PARADO. O app nunca pode travar.
            self._tell(f"Erro: {error}")
        finally:
            self.state = IDLE
