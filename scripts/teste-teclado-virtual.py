# Teste da Fase 0: cria um teclado virtual e digita a letra "a".
# Rode com o Python do venv e deixe o terminal em foco.
import time

import evdev

e = evdev.ecodes
teclado = evdev.UInput()
time.sleep(1)  # espera o GNOME reconhecer o teclado novo
teclado.write(e.EV_KEY, e.KEY_A, 1)  # aperta "a"
teclado.write(e.EV_KEY, e.KEY_A, 0)  # solta "a"
teclado.syn()
time.sleep(0.1)  # dá tempo da tecla chegar antes de fechar
teclado.close()
