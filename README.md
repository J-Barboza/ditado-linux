# Ditado

Ditado por voz para Linux. Segure a tecla **Pause**, fale e solte: o texto
aparece na janela em foco (terminal, navegador, editor…), com acentos e "ç"
corretos.

- Funciona offline: a transcrição roda no seu computador, com o Whisper.
- Idioma padrão: português.
- Roda em segundo plano e inicia sozinho quando você entra na sessão.
- Funciona no GNOME com X11 ou Wayland.

---

## 1. Requisitos

- RHEL 9 (ou compatível) com GNOME.
- Repositório **EPEL** ativado.
- **Python 3.13** do EPEL. Se não estiver instalado:
  ```bash
  sudo dnf install python3.13
  ```
- Um microfone configurado como entrada padrão em **Configurações → Som**.
- Cerca de **1 GB** livre: ~500 MB para o modelo de voz e o restante para as bibliotecas.
- Internet **só na instalação** e no primeiro uso (para baixar o modelo).

---

## 2. Instalação

Na pasta do projeto, rode **como seu usuário** (sem `sudo`):

```bash
./scripts/install.sh
```

O script pede a sua senha nas partes que precisam de administrador e:

1. instala os pacotes do sistema: `wl-clipboard`, `xclip`, `libnotify` e `portaudio`;
2. coloca seu usuário no grupo `input` (necessário para ler a tecla Pause);
3. libera o teclado virtual que o Ditado usa para colar o texto (`/dev/uinput`);
4. cria o ambiente Python em `~/.local/share/ditado/venv` e instala o Ditado;
5. cria o comando `ditado` em `~/.local/bin`;
6. instala e inicia o serviço que roda o Ditado em segundo plano.

**Se o script disser que adicionou você ao grupo `input`**, saia da sessão e
entre de novo. Sem isso, o Ditado não consegue ler a tecla Pause.

Na primeira vez que o Ditado inicia, ele baixa o modelo de voz (~460 MB).
Pode levar alguns minutos, dependendo da internet.

### Conferir a instalação

```bash
systemctl --user status ditado
```

Deve aparecer `active (running)`. Pronto: já dá para ditar.

---

## 3. Como usar

1. Clique na janela onde quer o texto.
2. **Segure Pause.** Você ouve um bip agudo e aparece a notificação "Gravando…".
3. **Fale.**
4. **Solte Pause.** Bip grave, notificação "Transcrevendo…" e, em cerca de 1 a 2
   segundos, o texto é colado.

Detalhes:

- Um espaço é colocado no fim do texto, para que dois ditados seguidos não
  fiquem grudados.
- O que estava na área de transferência antes do ditado é devolvido logo
  depois da colagem. Só texto é devolvido (uma imagem copiada se perde).
- Um toque rápido em Pause (menos de 0,3 s) é ignorado.
- Enquanto um ditado está sendo transcrito, a tecla Pause é ignorada.
- Funciona com qualquer teclado que tenha a tecla Pause, inclusive um teclado
  USB conectado depois.

### Modo alternar

Se preferir não segurar a tecla: um toque em Pause começa a gravar e outro
toque para. Veja a opção `modo` na [configuração](#5-configuração).

---

## 4. Comandos de voz

Fale o comando no meio do ditado:

| Você fala | Resultado |
|---|---|
| "vírgula" | `,` |
| "ponto final" | `.` |
| "ponto de interrogação" | `?` |
| "ponto de exclamação" | `!` |
| "dois pontos" | `:` |
| "nova linha" | quebra de linha |

Exemplo: "olá vírgula tudo bem ponto de interrogação" → `Olá, tudo bem?`

- Comandos seguidos ficam juntos: três vezes "ponto de exclamação" → `!!!`.
- Depois de `.`, `?`, `!` e de uma nova linha, a frase seguinte começa com
  letra maiúscula.
- **Cuidado no terminal:** "nova linha" equivale a apertar Enter, ou seja,
  executa o comando que estiver digitado.
- Os comandos estão sempre ligados. Se você falar "vírgula" querendo a
  palavra, ela vira `,`.

---

## 5. Configuração

O Ditado funciona sem configuração. Para mudar algo, crie o arquivo
`~/.config/ditado/config.toml` só com as opções que quer mudar. O que não
estiver no arquivo usa o valor padrão.

Todas as opções, com os valores padrão:

```toml
[atalho]
tecla = "KEY_PAUSE"       # tecla do atalho (nomes do evdev, ex.: "KEY_SCROLLLOCK")
modo = "segurar"          # "segurar" ou "alternar"

[audio]
dispositivo = ""          # vazio = microfone padrão do sistema

[whisper]
modelo = "small"          # "base" (mais rápido), "small", "medium", "large-v3-turbo" (mais preciso)
idioma = "pt"

[saida]
colar_com = "ctrl+shift+v"   # combinação para colar (ex.: "ctrl+v")
espaco_no_final = true       # espaço depois do texto colado
restaurar_clipboard = true   # devolve o conteúdo anterior da área de transferência

[avisos]
notificacao = true        # notificações na tela
bip = true                # bip ao começar e ao parar
```

Exemplo, para usar o modo alternar sem bip:

```toml
[atalho]
modo = "alternar"

[avisos]
bip = false
```

**Depois de mudar o arquivo, reinicie o serviço:**

```bash
systemctl --user restart ditado
```

Notas:

- `colar_com`: `ctrl+shift+v` cola no terminal e no navegador. Se algum
  programa não colar, experimente `ctrl+v`. Teclas aceitas: `ctrl`, `shift`,
  `alt`, `super` e as letras/teclas comuns (ex.: `v`, `insert`).
- `modelo`: um modelo diferente é baixado no primeiro uso. Modelos maiores
  acertam mais, mas demoram mais para transcrever e usam mais memória.
- Se o arquivo tiver um erro (opção com nome errado, sintaxe inválida), o
  Ditado não inicia e mostra o erro. Veja os [logs](#7-serviço-e-logs).

---

## 6. Atalho do GNOME (alternativa à tecla Pause)

O comando `ditado toggle` começa ou para a gravação, como um toque no modo
alternar. Use-o se a leitura da tecla Pause não funcionar no seu computador,
ligando-o a um atalho do GNOME:

1. **Configurações → Teclado → Atalhos de teclado → Ver e personalizar atalhos
   → Atalhos personalizados → +**
2. Nome: `Ditado`
3. Comando (troque `SEU_USUARIO` pelo seu usuário):
   ```
   /home/SEU_USUARIO/.local/bin/ditado toggle
   ```
4. Atalho: escolha uma tecla **diferente de Pause**. Se o Ditado também estiver
   lendo a Pause, as duas formas disparariam juntas.

---

## 7. Serviço e logs

O Ditado roda como um serviço do seu usuário:

| Para… | Comando |
|---|---|
| ver se está rodando | `systemctl --user status ditado` |
| reiniciar (ex.: depois de mudar a configuração) | `systemctl --user restart ditado` |
| parar até o próximo login | `systemctl --user stop ditado` |
| iniciar | `systemctl --user start ditado` |
| não iniciar mais no login | `systemctl --user disable ditado` |
| voltar a iniciar no login | `systemctl --user enable ditado` |
| acompanhar os logs | `journalctl --user-unit=ditado -f` |

Os logs mostram só o estado ("Gravando…", "Transcrevendo…", "Colado.") e os
teclados encontrados. **O texto ditado e as teclas digitadas nunca são
registrados.**

Para rodar no terminal em vez do serviço (útil para ver as mensagens na hora),
pare o serviço antes, porque só pode haver um Ditado rodando:

```bash
systemctl --user stop ditado
ditado run
```

---

## 8. Comandos de teste

Para verificar cada parte separadamente:

| Comando | O que faz |
|---|---|
| `ditado test-mic` | grava 3 s e mostra o volume do microfone |
| `ditado test-key` | mostra "apertou"/"soltou" ao usar a tecla Pause (Ctrl+C para sair) |
| `ditado test-transcribe arquivo.wav` | transcreve um arquivo de áudio e mostra o texto |
| `ditado test-paste` | depois de 3 s, cola "Olá, ação, coração" na janela em foco |

O `test-transcribe` precisa de um `.wav` de 16 kHz, mono. Para gravar um:

```bash
pw-record --rate 16000 --channels 1 teste.wav   # fale e aperte Ctrl+C
ditado test-transcribe teste.wav
```

---

## 9. Problemas comuns

| Problema | Solução |
|---|---|
| Aparece "Gravação muito curta, ignorada" | No modo `segurar`, é preciso **segurar** Pause enquanto fala. Para tocar e soltar, use o modo `alternar`. |
| Nada acontece ao apertar Pause | Rode `ditado test-key`. Se nenhum teclado aparecer em "Escutando", confira se você está no grupo `input` (`id -nG`) e se saiu e entrou na sessão depois da instalação. |
| "Nada reconhecido" | Rode `ditado test-mic`. Se o volume estiver perto de zero, escolha o microfone certo em **Configurações → Som**. |
| O texto não cola em um programa | Esse programa pode não usar Ctrl+Shift+V. Mude `colar_com` para `"ctrl+v"`. |
| Às vezes não cola no terminal | Acontece raramente. Repita o ditado. |
| O serviço falha com "já está rodando" | Há um `ditado run` aberto em algum terminal. Feche-o e rode `systemctl --user reset-failed ditado` e `systemctl --user start ditado`. |
| O serviço não inicia depois de mudar a configuração | Há um erro no `config.toml`. Veja a mensagem com `journalctl --user-unit=ditado -n 20`. |
| `journalctl --user -u ditado` diz "No journal files were found" | Use `journalctl --user-unit=ditado`. |
| O notebook não tem tecla Pause | Descubra o nome de outra tecla com `~/.local/share/ditado/venv/bin/python -m evdev.evtest` (escolha o teclado, aperte a tecla e veja o nome, ex.: `KEY_SCROLLLOCK`). Depois coloque esse nome em `tecla` na configuração. |
| Transcrição lenta | Use `modelo = "base"`. |

---

## 10. Desinstalar

```bash
systemctl --user disable --now ditado
rm ~/.config/systemd/user/ditado.service
systemctl --user daemon-reload
rm ~/.local/bin/ditado
rm -rf ~/.local/share/ditado ~/.config/ditado
rm -rf ~/.cache/huggingface/hub/models--Systran--faster-whisper-*
sudo rm /etc/udev/rules.d/80-ditado-uinput.rules
```

Os pacotes do sistema (`wl-clipboard`, `xclip`, `libnotify`, `portaudio`) e o
grupo `input` não são removidos, porque outros programas podem usá-los.
