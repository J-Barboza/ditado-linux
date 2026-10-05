"""Avisos: notificação na tela (notify-send) e bip curto."""

import subprocess

import numpy as np
import sounddevice as sd

BEEP_RATE = 44100  # taxa da placa de som para tocar o bip
BEEP_SECONDS = 0.08


class Notifier:
    def __init__(self, notifications=True, beep=True):
        self.notifications = notifications
        self.beep_enabled = beep

    def notify(self, message):
        if not self.notifications:
            return
        # Popen não espera o notify-send terminar, para não atrasar o ditado.
        # "transient" pede ao GNOME para não guardar o aviso na lista de notificações.
        try:
            subprocess.Popen(["notify-send", "-a", "Ditado", "-h", "int:transient:1", "Ditado", message])
        except OSError as error:
            print(f"Não foi possível mostrar a notificação: {error}")

    def beep(self, frequency):
        """Toca um bip curto. Agudo (880 Hz) para começar, grave (440 Hz) para parar."""
        if not self.beep_enabled:
            return
        # Uma onda senoidal: sin(2·π·frequência·tempo), com volume baixo (0.2)
        t = np.arange(int(BEEP_SECONDS * BEEP_RATE)) / BEEP_RATE
        tone = (0.2 * np.sin(2 * np.pi * frequency * t)).astype(np.float32)
        try:
            sd.play(tone, BEEP_RATE)  # toca em segundo plano, não espera acabar
        except Exception as error:
            print(f"Não foi possível tocar o bip: {error}")
