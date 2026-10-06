"""Comandos de voz: troca "vírgula", "ponto final", "nova linha"... pelo símbolo.

O Whisper costuma colocar pontuação própria em volta do comando
(ex.: "tudo bem, ponto final."). Essa pontuação extra é descartada.
"""

import re

# [ií] aceita a palavra com ou sem acento; [çc] e [ãa] idem
PUNCTUATION_COMMANDS = {
    r"v[ií]rgula": ",",
    r"ponto final": ".",
    r"ponto de interroga[çc][ãa]o": "?",
    r"ponto de exclama[çc][ãa]o": "!",
    r"dois pontos": ":",
}
NEW_LINE_COMMAND = r"nova linha"

# Espaços e pontuação que o Whisper põe em volta do comando
AROUND = r"[\s,.;:!?]*"
# Antes de "nova linha" só descartamos vírgulas: um ponto final ali é do texto
BEFORE_NEW_LINE = r"[\s,;:]*"


def _pattern(command, before):
    # \b = fronteira de palavra: o comando não casa no meio de outra palavra.
    # Os parênteses guardam o comando encontrado em match.group(1).
    return re.compile(before + r"\b(" + command + r")\b" + AROUND, re.IGNORECASE)


# Todos os comandos de pontuação num padrão só ("a|b|c"), para trocar tudo numa
# passada. Em passadas separadas, a pontuação que um comando acabou de colocar
# seria descartada pelo comando seguinte ("? !" viraria só "!").
_PUNCTUATION_PATTERN = _pattern("|".join(PUNCTUATION_COMMANDS), AROUND)
_NEW_LINE_PATTERN = _pattern(NEW_LINE_COMMAND, BEFORE_NEW_LINE)
# Espaço entre dois símbolos seguidos (ex.: "! ! !" de três comandos)
_SPACE_BETWEEN_SYMBOLS = re.compile(r"([,.?!:]) (?=[,.?!:])")
# Uma letra logo depois de ". ", "? ", "! " ou de uma quebra de linha
_SENTENCE_START = re.compile(r"([.!?] |\n)(\w)")


def _symbol_for(match):
    """Descobre qual comando foi encontrado e devolve o símbolo dele."""
    spoken = match.group(1)
    for command, symbol in PUNCTUATION_COMMANDS.items():
        if re.fullmatch(command, spoken, re.IGNORECASE):
            return symbol + " "


def apply_commands(text):
    text = _PUNCTUATION_PATTERN.sub(_symbol_for, text)
    text = _SPACE_BETWEEN_SYMBOLS.sub(r"\1", text)  # "! ! !" -> "!!!"
    text = _NEW_LINE_PATTERN.sub("\n", text)
    # Começo de frase com maiúscula
    text = _SENTENCE_START.sub(lambda match: match.group(1) + match.group(2).upper(), text)
    return text.strip(" ")
