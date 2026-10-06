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
    # \b = fronteira de palavra: o comando não casa no meio de outra palavra
    return re.compile(before + r"\b(?:" + command + r")\b" + AROUND, re.IGNORECASE)


_PUNCTUATION_PATTERNS = [
    (_pattern(command, AROUND), symbol) for command, symbol in PUNCTUATION_COMMANDS.items()
]
_NEW_LINE_PATTERN = _pattern(NEW_LINE_COMMAND, BEFORE_NEW_LINE)
# Uma letra logo depois de ". ", "? ", "! " ou de uma quebra de linha
_SENTENCE_START = re.compile(r"([.!?] |\n)(\w)")


def apply_commands(text):
    for pattern, symbol in _PUNCTUATION_PATTERNS:
        text = pattern.sub(symbol + " ", text)
    text = _NEW_LINE_PATTERN.sub("\n", text)
    # Começo de frase com maiúscula
    text = _SENTENCE_START.sub(lambda match: match.group(1) + match.group(2).upper(), text)
    return text.strip(" ")
