"""Socket Unix para o comando "ditado toggle".

Útil para ligar a um atalho personalizado do GNOME, caso a leitura do teclado
com evdev não funcione. O GNOME não avisa quando a tecla é solta, então por
aqui só existe o modo alternar (aperta para começar, aperta para parar).
"""

import os
import socket
import threading
from pathlib import Path


def socket_path():
    # XDG_RUNTIME_DIR (ex.: /run/user/1000) é uma pasta só do meu usuário
    return Path(os.environ["XDG_RUNTIME_DIR"]) / "ditado.sock"


def _connect():
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(str(socket_path()))
    return client


def serve(on_toggle):
    """Começa a escutar comandos numa thread em segundo plano."""
    path = socket_path()
    try:
        _connect().close()
        raise SystemExit(
            "O ditado já está rodando em outro terminal ou no serviço "
            "(systemctl --user status ditado)."
        )
    except (FileNotFoundError, ConnectionRefusedError):
        path.unlink(missing_ok=True)  # arquivo que sobrou de uma execução anterior

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(str(path))
    os.chmod(path, 0o600)  # só o meu usuário pode mandar comandos
    server.listen()

    def loop():
        while True:
            connection, _ = server.accept()
            with connection:
                try:
                    command = connection.recv(64).decode().strip()
                    if not command:
                        continue  # conexão vazia: alguém só conferiu se o app está rodando
                    if command != "toggle":
                        connection.sendall(b"comando desconhecido\n")
                        continue
                    on_toggle()
                    connection.sendall(b"ok\n")
                except Exception as error:  # a thread do socket nunca pode morrer
                    print(f"Erro no comando recebido pelo socket: {error}")

    threading.Thread(target=loop, daemon=True).start()


def send(command):
    """Manda um comando para o app que está rodando e devolve a resposta."""
    try:
        client = _connect()
    except (FileNotFoundError, ConnectionRefusedError):
        raise SystemExit("O ditado não está rodando. Inicie com: ditado run")
    with client:
        client.sendall(command.encode() + b"\n")
        return client.recv(64).decode().strip()
