"""Cola o texto na janela em foco: área de transferência + Ctrl+Shift+V.

Não "digitamos" letra por letra porque, no Wayland, um teclado virtual
erra os acentos. Copiar e colar preserva "ação", "coração" etc.
"""

import os
import subprocess
import time

import evdev
from evdev import ecodes

from ditado.config import ConfigError

KEY_DELAY = 0.012  # segundos entre uma tecla e outra
# Depois do Ctrl+V, o programa de destino ainda vai buscar o texto na área de
# transferência. Esperamos um pouco antes de devolver o conteúdo antigo.
RESTORE_DELAY = 0.5

MODIFIERS = {
    "ctrl": ecodes.KEY_LEFTCTRL,
    "shift": ecodes.KEY_LEFTSHIFT,
    "alt": ecodes.KEY_LEFTALT,
    "super": ecodes.KEY_LEFTMETA,
}


def parse_keys(combo):
    """Converte "ctrl+shift+v" em [KEY_LEFTCTRL, KEY_LEFTSHIFT, KEY_V]."""
    keys = []
    for name in combo.lower().split("+"):
        name = name.strip()
        if name in MODIFIERS:
            keys.append(MODIFIERS[name])
        elif "KEY_" + name.upper() in ecodes.ecodes:
            keys.append(ecodes.ecodes["KEY_" + name.upper()])
        else:
            raise ConfigError(f"Tecla desconhecida em saida.colar_com: {name!r}")
    return keys


def _is_wayland():
    return bool(os.environ.get("WAYLAND_DISPLAY"))


def copy_to_clipboard(text):
    if _is_wayland():
        command = ["wl-copy"]
    else:
        command = ["xclip", "-selection", "clipboard"]
    subprocess.run(command, input=text.encode("utf-8"), check=True)


def read_clipboard():
    """Devolve o texto da área de transferência, ou None se não houver texto
    (vazia, ou com uma imagem, por exemplo)."""
    if _is_wayland():
        command = ["wl-paste", "--no-newline"]
    else:
        command = ["xclip", "-o", "-selection", "clipboard"]
    try:
        result = subprocess.run(command, capture_output=True, timeout=2)
        if result.returncode != 0:
            return None
        return result.stdout.decode("utf-8")
    except (subprocess.TimeoutExpired, UnicodeDecodeError):
        return None


class Paster:
    def __init__(self, keys, restore_clipboard=True):
        self.keys = keys  # combinação de colar, ex.: parse_keys("ctrl+shift+v")
        self.restore_clipboard = restore_clipboard
        # Teclado virtual criado em /dev/uinput (precisa da regra udev do install.sh).
        # Criamos uma vez só: o GNOME demora um pouco para reconhecer um teclado novo.
        # Ele só tem as teclas de colar; sem a tecla Pause, o hotkey.py não o escuta.
        self.keyboard = evdev.UInput({ecodes.EV_KEY: keys}, name="ditado-teclado-virtual")
        time.sleep(0.5)

    def _press_keys(self, keys):
        # Aperta as teclas na ordem e solta na ordem inversa (como uma pessoa faria)
        for key in keys:
            self._send_key(key, 1)
        for key in reversed(keys):
            self._send_key(key, 0)

    def _send_key(self, key, value):
        self.keyboard.write(ecodes.EV_KEY, key, value)
        self.keyboard.syn()
        # Pausa curta entre as teclas (o ydotool usa 12 ms). Sem ela, às vezes o
        # "V" chega antes de o sistema registrar o Ctrl+Shift, e a colagem falha.
        time.sleep(KEY_DELAY)

    def paste(self, text):
        previous = read_clipboard() if self.restore_clipboard else None
        copy_to_clipboard(text)
        self._press_keys(self.keys)
        if previous is not None:
            time.sleep(RESTORE_DELAY)
            copy_to_clipboard(previous)

    def close(self):
        time.sleep(0.1)  # dá tempo das teclas chegarem antes de fechar
        self.keyboard.close()
