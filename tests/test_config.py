import pytest

from ditado.config import DEFAULTS, ConfigError, load_config


def test_sem_arquivo_usa_os_padroes(tmp_path):
    assert load_config(tmp_path / "nao_existe.toml") == DEFAULTS


def test_arquivo_sobrescreve_so_o_que_tem(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text('[whisper]\nmodelo = "base"\n\n[avisos]\nbip = false\n')

    config = load_config(path)

    assert config["whisper"]["modelo"] == "base"
    assert config["avisos"]["bip"] is False
    assert config["whisper"]["idioma"] == "pt"  # continua o padrão
    assert config["saida"] == DEFAULTS["saida"]


def test_nao_altera_os_padroes(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text('[whisper]\nmodelo = "base"\n')
    load_config(path)
    assert DEFAULTS["whisper"]["modelo"] == "small"


def test_opcao_desconhecida_da_erro(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text('[whisper]\nmodelos = "base"\n')  # erro de digitação
    with pytest.raises(ConfigError, match="whisper.modelos"):
        load_config(path)


def test_modo_invalido_da_erro(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text('[atalho]\nmodo = "apertar"\n')
    with pytest.raises(ConfigError, match="atalho.modo"):
        load_config(path)


def test_erro_de_sintaxe_vira_config_error(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text('[whisper\nmodelo = "base"\n')  # falta o "]"
    with pytest.raises(ConfigError, match="sintaxe"):
        load_config(path)
