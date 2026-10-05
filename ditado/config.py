"""Lê ~/.config/ditado/config.toml. O que não estiver no arquivo usa o valor padrão."""

import copy
import tomllib  # leitor de TOML da biblioteca padrão (Python 3.11+)
from pathlib import Path

CONFIG_PATH = Path.home() / ".config" / "ditado" / "config.toml"

DEFAULTS = {
    "atalho": {
        "tecla": "KEY_PAUSE",
        "modo": "segurar",  # "segurar" ou "alternar"
    },
    "audio": {
        "dispositivo": "",  # vazio = microfone padrão do sistema
    },
    "whisper": {
        "modelo": "small",
        "idioma": "pt",
        "dispositivo": "auto",  # por enquanto sempre CPU; a GPU fica para a fase 5
    },
    "saida": {
        "colar_com": "ctrl+shift+v",
        "espaco_no_final": True,
        "restaurar_clipboard": True,
    },
    "avisos": {
        "notificacao": True,
        "bip": True,
    },
}


def load_config(path=CONFIG_PATH):
    """Devolve a configuração: os padrões, sobrescritos pelo que houver no arquivo."""
    config = copy.deepcopy(DEFAULTS)  # cópia, para não alterar os padrões
    if not path.exists():
        return config

    with open(path, "rb") as file:
        user_config = tomllib.load(file)

    for section, values in user_config.items():
        if section not in config:
            raise ValueError(f"Seção desconhecida em {path}: [{section}]")
        for key, value in values.items():
            if key not in config[section]:
                raise ValueError(f"Opção desconhecida em {path}: {section}.{key}")
            config[section][key] = value

    if config["atalho"]["modo"] not in ("segurar", "alternar"):
        raise ValueError('atalho.modo precisa ser "segurar" ou "alternar"')
    return config
