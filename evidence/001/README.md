# Evidência da spec 001 — 16/11/2026

Investigação adicional: [captura USB bruta e interface de diagnóstico](usb-investigation.md).

Revisão atual de código/diff, nove testes e nova comparação física:
[review/README.md](review/README.md). CA-01 continua parcial por ausência de
origens independentes L4/R4; Share foi acompanhado até a saída real uinput.

## Hardware e ambiente

- CachyOS, kernel `7.3.3-1-cachyos`.
- USB `3537:1010`, produto GameSir-G7 SE Controller for Xbox.
- `bcdDevice 6.38`: descritor USB, não uma versão de firmware confirmada por consulta proprietária.
- Modo GIP: interfaces `ff/47/d0`; driver observado `xone-wired`.
- Entrada inicial `/dev/input/event27`, nome Microsoft Xbox Controller.
- evtest ausente no sistema: compilado em `/tmp/gamesr-evtest` a partir do
  [fonte oficial](https://gitlab.freedesktop.org/libevdev/evtest/-/raw/master/evtest.c).
  Cópia em `evtest.c`, SHA256 `54c6ee1057d55de128ff4f102a48036ce7b04e85cdd59bd8c29026cccf6650c5`.
- Sem alteração de firmware ou perfil embarcado. Na investigação USB adicional,
  o alternate setting da interface 2 foi alterado temporariamente e restaurado;
  o driver principal xone foi preservado. Xbox + Share causou reinício físico,
  voltando à mesma identidade estável. Detalhes no relatório USB.

## Captura física por botão

Comando: `timeout 55s stdbuf -oL /tmp/gamesr-evtest /dev/input/event27`.
Sequência solicitada: A, B, L4, R4, Share sozinho, três ciclos cada.
Usuário confirmou toda a sequência com travas traseiras habilitadas.
Log integral: [evtest-buttons.txt](evtest-buttons.txt).

| Botão | Press | Release | Resultado |
|---|---|---|---|
| A | EV_KEY 304 BTN_SOUTH, 1, 3 vezes | Mesmo código, 0, 3 vezes | Referência independente de B/Share |
| B | EV_KEY 305 BTN_EAST, 1, 3 vezes | Mesmo código, 0, 3 vezes | Referência independente de A/Share |
| L4 | Nenhum evento no intervalo informado | Nenhum | Captura independente não demonstrada; não mapear |
| R4 | Nenhum evento no intervalo informado | Nenhum | Captura independente não demonstrada; não mapear |
| Share | EV_KEY 167 KEY_RECORD, 1, 3 vezes | Mesmo código, 0, 3 vezes | Distinto de A/B; elegível para F11 |

A ausência de eventos de L4/R4 neste ensaio não prova impossibilidade em outros
modos ou perfis. O evtest anuncia apenas os códigos convencionais e KEY_RECORD,
sem códigos separados de paddles. Não foi observado alias de L4/R4 com A/B nesta coleta.

## Investigação do Deadband

Fonte: [gamesir-linux-tools](https://github.com/broroeror/gamesir-linux-tools),
commit `3de56e8945ec1f99f4a4b7553af89564b3bb88bd`.
Cópias dos trechos consultados em `deadband/`.

- `vendors/gamesir/models/g7se/protocol.py`: VID:PID `3537:1010`;
  layouts conhecidos `0x0630` e `0x0664`; `select()` rejeita descritor desconhecido.
  O observado `0x0638` não consta nesses layouts.
- `vendors/gamesir/models/g7se/input.py`: `decode()` lê comando GIP `0x20`,
  botões convencionais, eixos e direcional. Não decodifica origens L4/R4/Share.
- `reader.py`, `read_session_seusb()`: usa esse decoder e assume o canal USB
  durante configuração, indicando controle indisponível para jogos.
- Os slots de remapeamento embarcado de L4/R4 não demonstram uma captura
  independente desses botões no fluxo de entrada. O parser enhanced genérico
  anunciado para outros modelos não pode ser aplicado automaticamente ao G7 SE.

Portanto essa revisão do Deadband não fornece uma leitura independente comprovada
para L4/R4 nesta identidade/descritor. Nenhuma escrita proprietária foi executada.

## Mapeador e próximos testes

`tools/map_buttons.py` usa python-evdev e uinput. A configuração persistente está
em `config/mapping.json`. Somente Share/KEY_RECORD está autorizado como origem.
L4→F9 e R4→F10 são recusados até existir evidência física de origens distintas.

O mapeador não usa EVIOCGRAB: o controle convencional continua disponível.
Isso também preserva o evento Share original; duplicidade no Steam depende do
perfil Steam Input/jogo e ainda precisa de teste físico. Não se afirma supressão
seletiva do evento original.

Proteções implementadas: ignorar repetições e presses duplicados, liberar teclas
no desligamento/desconexão/SYN_DROPPED, redescobrir por VID:PID após reconexão,
ignorar botão já segurado ao reconectar até sua soltura. Essas proteções precisam
ser diferenciadas de testes físicos aprovados.

Execução: `python tools/map_buttons.py`. Dependência: `python-evdev`.
Precisa de leitura do event do controle e escrita em `/dev/uinput`.
Bloqueio de instância única via flock impede dois mapeadores simultâneos
na mesma sessão de usuário. Rejeição de segunda instância verificada em
`single-instance.txt`.

`output_mode` aceita `hold` (tecla mantida até soltura física) ou `tap` (um par
curto de press/release por pressão física, sem manter a tecla). O arquivo salvo
usa `tap` após a investigação de repetição de capturas no Steam. Ver
[validação Steam](steam-validation.md) para contagens, limitações e resultado.

Saída real observada em `uinput-share-session2.txt`: quatro ciclos de
`EV_KEY 87 KEY_F11` (1/0), correspondendo a quatro ciclos `KEY_RECORD` no
prefixo válido de `evtest-source-session2.txt`. Não houve presses adicionais
no teclado virtual. O quarto ciclo foi o teste segurando Share.

Na desconexão, a entrada física enviou release antes de retornar ENODEV.
Portanto este ensaio demonstra F11 liberado, mas não exercita o ramo de limpeza
com uma tecla ainda presente no conjunto interno de teclas seguradas.
O mapeador registrou `disconnected` e depois `connected ... blocked=[167]`,
comprovando redescoberta sem reinício e detecção de Share segurado ao reconectar.

Limitação dos logs: o evtest compilado falhou ao ler dispositivos removidos,
imprimindo dados inválidos e, em um caso, terminando com core dump. Em
`evtest-source-session2.txt`, somente eventos anteriores ao primeiro
registro inválido (timestamp/código impossível) têm valor probatório.
`uinput-share-continued.txt` também perdeu validade após a remoção do primeiro
teclado virtual durante o reinício planejado da sessão. Esses sufixos não são
eventos reais do controle. O observador `uinput-share-session2.txt` permanece
no teclado virtual da segunda sessão, que não foi removido na reconexão USB.

CA-01: parcial (Share→F11 observado fisicamente; L4/R4 pendentes).
CA-02: aprovado para Share. Configuração salva como KEY_F10, processo anterior
encerrado e novo processo iniciado lendo o arquivo. `evtest-persistence-source.txt`
registra A (304), B (305), Share (167), um ciclo cada, e
`uinput-persistence-f10.txt` registra somente um ciclo F10 (68), sincronizado
com Share. A/B não emitiram teclas mapeadas. Configuração depois restaurada a F11.
L4/R4 não puderam ser testados.
CA-03: aprovado para Share no cenário físico executado: F11 liberado,
reconexão detectada sem reinício e novos ciclos F11 depois da reconexão,
registrados no mesmo `uinput-share-session2.txt`. O usuário confirmou a execução
segurando Share ao desconectar/reconectar. L4/R4 pendentes.
CA-04: aprovado para Share como captura do Steam durante The Elder Scrolls V:
Skyrim Special Edition, com Steam Input desabilitado (imagem: compatibilidade
nativa). Modo tap: três pressões, três pares F11, três capturas novas, A/B
normais e nenhum segundo comando segundo o usuário. A tentativa anterior de
associar tecla a gameplay ficou bloqueada porque a tela do Skyrim recusou
teclado físico e L4/R4/Share. A ação validada é do Steam durante o jogo;
não se afirma aceitação de teclado para gameplay. L4/R4 pendentes.
CA-05: origens sem comprovação são recusadas e diagnóstico inclui VID:PID/modo;
critério funcional de L4/R4 permanece pendente.

### Complemento: conclusão do teste Steam para Share

O bloqueio da tela de controles do Skyrim foi contornado usando o atalho de
captura de tela do próprio Steam como ação local F11. A primeira rodada em
hold gerou quatro capturas para três pressões, compatível com repetição do
atalho em uma pressão longa. Após adicionar modo configurável tap e usá-lo,
foram observados três pares F11 e exatamente três arquivos novos para três
pressões, incluindo uma de ~2,1 s. Usuário confirmou A/B normais e nenhum
segundo comando. Portanto CA-04 está aprovado para Share nessa ação e com
Steam Input desabilitado; não comprova ação de gameplay por teclado no Skyrim.
Detalhes e evidências em [steam-validation.md](steam-validation.md).

Resultado global da spec: parcial. CA-01/02/03/04 comprovados para Share nas
condições descritas; L4/R4 continuam pendentes. A captura USB passiva não
mostrou relatórios de entrada desses botões, mesmo após reinício, e a leitura
bulk sem comandos proprietários falhou sem dados. Nenhum mapeamento F9/F10
foi inventado para eles. Quatro testes de estado do mapeador passaram.

Limpeza concluída: processos temporários de captura e mapeamento encerrados,
teclas liberadas e módulo usbmon descarregado. Usuário confirmou restauração
do atalho Steam para F12. A configuração Share→F11/tap permanece salva;
nenhum serviço de inicialização automática foi instalado.
