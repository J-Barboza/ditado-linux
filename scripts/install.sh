#!/usr/bin/env bash
# Instala o que o Ditado precisa no RHEL 9.
# Rode como seu usuário normal (sem sudo): o script pede a senha só nas partes
# que exigem root. Pode ser rodado de novo sem problema.
set -euo pipefail

VENV="$HOME/.local/share/ditado/venv"
PYTHON=/usr/bin/python3.13
UDEV_RULE=/etc/udev/rules.d/80-ditado-uinput.rules

if [ "$(id -u)" -eq 0 ]; then
    echo "Não rode com sudo: o venv precisa pertencer ao seu usuário." >&2
    exit 1
fi

echo "==> Instalando pacotes do sistema (dnf)"
# portaudio: biblioteca que o sounddevice usa para gravar
# wl-clipboard (Wayland) e xclip (X11): copiam o texto para a área de transferência
# skip_if_unavailable: não deixa um repositório quebrado (ex.: pgdg) parar a instalação
sudo dnf install -y --setopt=skip_if_unavailable=True \
    wl-clipboard xclip libnotify portaudio

echo "==> Grupo input (para ler o teclado em /dev/input/event*)"
if id -nG "$USER" | grep -qw input; then
    echo "    $USER já está no grupo input."
else
    sudo usermod -aG input "$USER"
    echo "    Adicionado. Saia da sessão e entre de novo para valer."
fi

echo "==> Regra udev para o teclado virtual (/dev/uinput)"
# Dá ao grupo input permissão de escrita em /dev/uinput. É assim que o app
# "aperta" Ctrl+Shift+V para colar. Atenção: qualquer programa do grupo input
# passa a poder simular teclas.
echo 'KERNEL=="uinput", SUBSYSTEM=="misc", GROUP="input", MODE="0660", OPTIONS+="static_node=uinput"' \
    | sudo tee "$UDEV_RULE" > /dev/null
sudo udevadm control --reload-rules
# A regra só é aplicada no próximo boot; estes comandos aplicam já.
sudo modprobe uinput
sudo chgrp input /dev/uinput
sudo chmod 0660 /dev/uinput

echo "==> Ambiente Python (venv) em $VENV"
if [ ! -x "$VENV/bin/python" ]; then
    mkdir -p "$(dirname "$VENV")"
    "$PYTHON" -m venv "$VENV"
fi
"$VENV/bin/pip" install --upgrade pip
# Instala o Ditado e as dependências do pyproject.toml. O "-e" (editável) faz o
# venv usar o código desta pasta: uma mudança no código vale sem reinstalar.
# Obs.: o evdev vem do pacote evdev-binary (já compilado), assim não precisamos do
# python3.13-devel, que no EPEL exige um RHEL mais novo.
"$VENV/bin/pip" install -e "$(dirname "$0")/.."

echo "==> Comando ditado em ~/.local/bin"
mkdir -p "$HOME/.local/bin"
ln -sf "$VENV/bin/ditado" "$HOME/.local/bin/ditado"

echo "==> Serviço systemd de usuário (inicia o ditado no login)"
mkdir -p "$HOME/.config/systemd/user"
cp "$(dirname "$0")/../systemd/ditado.service" "$HOME/.config/systemd/user/"
systemctl --user daemon-reload
systemctl --user enable ditado
# restart (e não start): se já estava rodando, passa a usar o código novo
systemctl --user restart ditado

cat <<EOF

Pronto. O ditado já está rodando como serviço:
  systemctl --user status ditado
  journalctl --user -u ditado -f

Testes da Fase 0:
  1) Tecla Pause (escolha o teclado na lista e aperte Pause; Ctrl+C para sair):
     $VENV/bin/python -m evdev.evtest

  2) Teclado virtual (deve aparecer um "a" no terminal depois de 1 s):
     $VENV/bin/python $(dirname "$0")/teste-teclado-virtual.py
EOF
