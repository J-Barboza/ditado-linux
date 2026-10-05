"""Cola o texto na janela em foco: área de transferência + Ctrl+Shift+V.

Não "digitamos" letra por letra porque, no Wayland, um teclado virtual
erra os acentos. Copiar e colar preserva "ação", "coração" etc.
"""

import os
import subprocess
import time

import evdev
from evdev import ecodes

# Ctrl+Shift+V cola tanto no terminal quanto no navegador
PASTE_KEYS = [ecodes.KEY_LEFTCTRL, ecodes.KEY_LEFTSHIFT, ecodes.KEY_V]


def copy_to_clipboard(text):
    if os.environ.get("WAYLAND_DISPLAY"):
        command = ["wl-copy"]
    else:
        command = ["xclip", "-selection", "clipboard"]
    subprocess.run(command, input=text.encode("utf-8"), check=True)


class Paster:
    def __init__(self):
        # Teclado virtual criado em /dev/uinput (precisa da regra udev do install.sh).
        # Criamos uma vez só: o GNOME demora um pouco para reconhecer um teclado novo.
        self.keyboard = evdev.UInput(name="ditado-teclado-virtual")
        time.sleep(0.5)

    def _press_keys(self, keys):
        # Aperta as teclas na ordem e solta na ordem inversa (como uma pessoa faria)
        for key in keys:
            self.keyboard.write(ecodes.EV_KEY, key, 1)
            self.keyboard.syn()
        for key in reversed(keys):
            self.keyboard.write(ecodes.EV_KEY, key, 0)
            self.keyboard.syn()

    def paste(self, text):
        copy_to_clipboard(text)
        self._press_keys(PASTE_KEYS)

    def close(self):
        time.sleep(0.1)  # dá tempo das teclas chegarem antes de fechar
        self.keyboard.close()
