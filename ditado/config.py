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


class ConfigError(ValueError):
    """Erro no arquivo de configuração: mostrado ao usuário sem o traceback."""


def load_config(path=CONFIG_PATH):
    """Devolve a configuração: os padrões, sobrescritos pelo que houver no arquivo."""
    config = copy.deepcopy(DEFAULTS)  # cópia, para não alterar os padrões
    if not path.exists():
        return config

    with open(path, "rb") as file:
        try:
            user_config = tomllib.load(file)
        except tomllib.TOMLDecodeError as error:
            raise ConfigError(f"Erro de sintaxe em {path}: {error}")

    for section, values in user_config.items():
        if section not in config:
            raise ConfigError(f"Seção desconhecida em {path}: [{section}]")
        for key, value in values.items():
            if key not in config[section]:
                raise ConfigError(f"Opção desconhecida em {path}: {section}.{key}")
            config[section][key] = value

    if config["atalho"]["modo"] not in ("segurar", "alternar"):
        raise ConfigError('atalho.modo precisa ser "segurar" ou "alternar"')
    return config
