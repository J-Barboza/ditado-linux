"""Escuta a tecla de atalho (Pause) lendo o teclado direto do kernel com evdev.

Privacidade: o app recebe TODAS as teclas digitadas. Aqui tudo que não for a
tecla de atalho é descartado na hora, e nada é registrado em log.
"""

import selectors

import evdev
from evdev import ecodes


def find_keyboards(key=ecodes.KEY_PAUSE):
    """Devolve os dispositivos de entrada que têm a tecla pedida."""
    keyboards = []
    # list_devices() só lista os /dev/input/event* que temos permissão de ler
    for path in evdev.list_devices():
        device = evdev.InputDevice(path)
        keys = device.capabilities().get(ecodes.EV_KEY, [])
        if key in keys:
            keyboards.append(device)
        else:
            device.close()
    return keyboards


def listen(on_press, on_release, key=ecodes.KEY_PAUSE):
    """Fica esperando a tecla; chama on_press() ao apertar e on_release() ao soltar.

    Nunca usamos grab(): o resto do sistema continua recebendo as teclas.
    """
    keyboards = find_keyboards(key)
    if not keyboards:
        raise RuntimeError(
            "Nenhum teclado com a tecla de atalho foi encontrado. "
            "Seu usuário está no grupo input?"
        )

    # O selector espera vários teclados ao mesmo tempo, sem gastar CPU:
    # select() só retorna quando algum deles tem eventos para ler.
    selector = selectors.DefaultSelector()
    for keyboard in keyboards:
        selector.register(keyboard, selectors.EVENT_READ)

    while True:
        for selected, _ in selector.select():
            for event in selected.fileobj.read():
                if event.type != ecodes.EV_KEY or event.code != key:
                    continue  # outra tecla: ignora (privacidade)
                # value: 1 = apertou, 0 = soltou, 2 = repetição (tecla segurada)
                if event.value == 1:
                    on_press()
                elif event.value == 0:
                    on_release()
