import pytest

from ditado.commands import apply_commands


@pytest.mark.parametrize(
    "whisper, esperado",
    [
        # sem comandos: não muda nada
        ("Olá, ação, coração.", "Olá, ação, coração."),
        # o Whisper costuma cercar o comando com vírgulas e pontos
        ("Olá, vírgula, tudo bem, ponto final.", "Olá, tudo bem."),
        ("Tudo bem ponto de interrogação", "Tudo bem?"),
        ("Atenção, ponto de exclamação.", "Atenção!"),
        ("Lista dois pontos maçã", "Lista: maçã"),
        # maiúsculas e palavra sem acento
        ("Olá Virgula tudo bem Ponto Final", "Olá, tudo bem."),
        ("Tudo bem, ponto de interrogacao", "Tudo bem?"),
        # o Whisper já pôs o ponto e o comando repete: fica um só
        ("Como vai. Ponto final.", "Como vai."),
        # nova linha mantém o ponto que veio antes
        ("Primeira linha. Nova linha. Segunda linha.", "Primeira linha.\nSegunda linha."),
        ("Fim, ponto final. Nova linha. Tchau.", "Fim.\nTchau."),
        # maiúscula depois de ponto e de nova linha
        ("ok ponto final tudo bem", "ok. Tudo bem"),
        ("item um nova linha item dois", "item um\nItem dois"),
        # "pontos" sozinho não é comando; números com ponto não mudam
        ("Fiz três pontos no jogo, nota 3.5", "Fiz três pontos no jogo, nota 3.5"),
    ],
)
def test_apply_commands(whisper, esperado):
    assert apply_commands(whisper) == esperado


def test_termina_com_nova_linha():
    assert apply_commands("Tchau, nova linha.") == "Tchau\n"


def test_comandos_seguidos_ficam_juntos():
    assert apply_commands(
        "Funcionou, ponto de exclamação, ponto de exclamação, ponto de exclamação."
    ) == "Funcionou!!!"
    assert apply_commands("Sério ponto de interrogação ponto de exclamação") == "Sério?!"
