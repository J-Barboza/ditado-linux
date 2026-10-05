"""Escuta a tecla de atalho (Pause) lendo o teclado direto do kernel com evdev.

Privacidade: o app recebe TODAS as teclas digitadas. Aqui tudo que não for a
tecla de atalho é descartado na hora, e nada é registrado em log.
"""

import selectors

import evdev
from evdev import ecodes

RESCAN_SECONDS = 2  # de quanto em quanto tempo procurar teclados conectados depois


def _add_new_keyboards(selector, seen, key):
    """Registra no selector os teclados que apareceram desde a última procura."""
    # list_devices() só lista os /dev/input/event* que temos permissão de ler
    paths = set(evdev.list_devices())
    # Esquece os caminhos que sumiram: o kernel pode reaproveitá-los para outro aparelho
    seen.intersection_update(paths)
    for path in paths - seen:
        seen.add(path)  # examina cada aparelho uma vez só, tendo ou não a tecla
        try:
            device = evdev.InputDevice(path)
        except OSError:
            continue  # desconectado no meio do caminho
        if key in device.capabilities().get(ecodes.EV_KEY, []):
            selector.register(device, selectors.EVENT_READ)
            print(f"Escutando: {device.name} ({device.path})")
        else:
            device.close()


def listen(on_press, on_release, key=ecodes.KEY_PAUSE, warn=print):
    """Fica esperando a tecla; chama on_press() ao apertar e on_release() ao soltar.

    Teclados conectados depois são encontrados sozinhos (a cada RESCAN_SECONDS).
    Nunca usamos grab(): o resto do sistema continua recebendo as teclas.
    """
    # O selector espera vários teclados ao mesmo tempo, sem gastar CPU:
    # select() só retorna quando algum deles tem eventos para ler (ou no timeout).
    selector = selectors.DefaultSelector()
    seen = set()  # caminhos /dev/input/event* já examinados

    _add_new_keyboards(selector, seen, key)
    if not selector.get_map():
        warn(
            "Nenhum teclado com a tecla de atalho foi encontrado (ainda). "
            "Seu usuário está no grupo input?"
        )

    while True:
        for selected, _ in selector.select(timeout=RESCAN_SECONDS):
            device = selected.fileobj
            try:
                # read() devolve um gerador: o list() lê tudo aqui dentro do try,
                # senão o erro de "aparelho sumiu" só apareceria depois, fora dele
                events = list(device.read())
            except OSError:
                # O teclado foi desconectado: para de escutá-lo
                print(f"Teclado desconectado: {device.name}")
                selector.unregister(device)
                seen.discard(device.path)
                device.close()
                continue
            for event in events:
                if event.type != ecodes.EV_KEY or event.code != key:
                    continue  # outra tecla: ignora (privacidade)
                # value: 1 = apertou, 0 = soltou, 2 = repetição (tecla segurada)
                if event.value == 1:
                    on_press()
                elif event.value == 0:
                    on_release()
        _add_new_keyboards(selector, seen, key)
