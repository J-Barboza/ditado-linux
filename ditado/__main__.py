"""Linha de comando: ditado run | toggle | test-mic | test-key | test-transcribe | test-paste."""

import argparse
import sys
import time

# Os imports pesados (faster-whisper, sounddevice...) ficam dentro de cada
# comando, para que um comando não espere carregar o que não usa.


def cmd_run(args):
    from ditado.app import App
    from ditado.config import load_config

    App(load_config()).run()


def cmd_toggle(args):
    from ditado import ipc

    print(ipc.send("toggle"))
    return 0


def cmd_test_mic(args):
    import numpy as np
    import sounddevice as sd

    from ditado.audio import SAMPLE_RATE, Recorder

    # "default" = o microfone escolhido em Configurações → Som (via PipeWire)
    print(f"Microfone: {sd.query_devices(kind='input')['name']} (o padrão de Configurações → Som)")
    print("Gravando 3 segundos... fale alguma coisa!")
    recorder = Recorder()
    recorder.start()
    time.sleep(3)
    audio = recorder.stop()

    if audio.size == 0:
        print("Nenhum áudio foi gravado.")
        return 1
    # As amostras vão de -1.0 a 1.0; o pico é o ponto mais alto e o RMS é a média do volume
    peak = float(np.max(np.abs(audio)))
    rms = float(np.sqrt(np.mean(audio**2)))
    print(f"Duração: {audio.size / SAMPLE_RATE:.1f} s")
    print(f"Pico:  {peak:6.1%}  {'#' * int(peak * 40)}")
    print(f"Média: {rms:6.1%}  {'#' * int(rms * 40)}")
    if peak < 0.01:
        print("Quase silêncio: confira o microfone padrão em Configurações → Som.")
    return 0


def cmd_test_key(args):
    from ditado.hotkey import listen

    print("Aperte e solte a tecla Pause (Ctrl+C para sair).")
    listen(on_press=lambda: print("apertou"), on_release=lambda: print("soltou"))


def read_wav(path):
    """Lê um .wav de 16 kHz, mono, 16 bits e devolve um array float32 (como o do microfone)."""
    import wave

    import numpy as np

    with wave.open(path, "rb") as wav:
        if (wav.getframerate(), wav.getnchannels(), wav.getsampwidth()) != (16000, 1, 2):
            raise SystemExit(
                "O .wav precisa ser 16 kHz, mono, 16 bits. Grave com:\n"
                "  pw-record --rate 16000 --channels 1 teste.wav"
            )
        data = wav.readframes(wav.getnframes())
    # Amostras de 16 bits vão de -32768 a 32767; dividimos para ficar entre -1.0 e 1.0
    return np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768


def cmd_test_transcribe(args):
    from ditado.transcriber import Transcriber

    audio = read_wav(args.arquivo)

    print("Carregando o modelo (na primeira vez ele é baixado, pode demorar)...")
    start = time.monotonic()
    transcriber = Transcriber()
    print(f"Modelo carregado em {time.monotonic() - start:.1f} s")

    start = time.monotonic()
    text = transcriber.transcribe(audio)
    print(f"Transcrito em {time.monotonic() - start:.1f} s:")
    print(text or "(nada reconhecido)")
    return 0


def cmd_test_paste(args):
    from ditado.config import load_config
    from ditado.output import Paster, parse_keys

    saida = load_config()["saida"]
    paster = Paster(parse_keys(saida["colar_com"]), saida["restaurar_clipboard"])
    for seconds in (3, 2, 1):
        print(f"Colando em {seconds}... (clique na janela onde quer colar)")
        time.sleep(1)
    paster.paste("Olá, ação, coração")
    paster.close()
    return 0


def main():
    parser = argparse.ArgumentParser(prog="ditado", description="Ditado por voz")
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("run", help="segure Pause, fale e solte: o texto é colado").set_defaults(
        func=cmd_run
    )
    commands.add_parser("toggle", help="começa ou para a gravação no app que está rodando").set_defaults(
        func=cmd_toggle
    )
    commands.add_parser("test-mic", help="grava 3 s e mostra o volume").set_defaults(
        func=cmd_test_mic
    )
    commands.add_parser("test-key", help="mostra quando a tecla Pause é usada").set_defaults(
        func=cmd_test_key
    )
    transcribe = commands.add_parser("test-transcribe", help="transcreve um arquivo .wav")
    transcribe.add_argument("arquivo")
    transcribe.set_defaults(func=cmd_test_transcribe)
    commands.add_parser("test-paste", help="cola um texto de teste na janela em foco").set_defaults(
        func=cmd_test_paste
    )

    args = parser.parse_args()
    from ditado.config import ConfigError

    try:
        return args.func(args)
    except ConfigError as error:
        print(f"Erro na configuração: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print()  # Ctrl+C: sai sem mostrar erro
        return 0


if __name__ == "__main__":
    sys.exit(main())
