import pytest
from evdev import ecodes

from ditado.output import parse_keys


def test_combinacao_padrao():
    assert parse_keys("ctrl+shift+v") == [ecodes.KEY_LEFTCTRL, ecodes.KEY_LEFTSHIFT, ecodes.KEY_V]


def test_ignora_maiusculas_e_espacos():
    assert parse_keys("Ctrl + V") == [ecodes.KEY_LEFTCTRL, ecodes.KEY_V]


def test_tecla_desconhecida_da_erro():
    with pytest.raises(ValueError, match="ctlr"):
        parse_keys("ctlr+v")  # erro de digitação
