# Captura USB bruta — 16/11/2026

Unidade `3537:1010`, `bcdDevice=0638`, barramento 1/endereço 4,
porta `1-6`, driver `xone-wired`. Mapeador uinput desligado nesta investigação.

## Coleta passiva

Carregado o módulo `usbmon` e executado `dumpcap -i usbmon1 -a duration:150`.
O barramento continha o controle e seu hub raiz. O arquivo permanente
`usbmon-buttons.pcapng` foi filtrado offline para `usb.device_address == 4`.
Nenhuma interface foi reivindicada durante a coleta passiva.

Dados extraídos em `usbmon-payloads.tsv`, decodificação em
`usbmon-decoded.json`, marcações da interação em `usbmon-markers.jsonl`.
Cada marca inicial antecede a instrução enviada ao usuário; a marca de conclusão
é posterior à confirmação dele. São janelas de observação, não timestamps
individuais das pressões.

| Botão | Evidência USB |
|---|---|
| A | Report GIP `20 00 seq 20`, payload byte 0 = `10`; release payload zerado |
| B | Mesmo comando, payload byte 0 = `20`; release payload zerado |
| Share | Mesmo comando, payload byte 14 = `01` (offset 18 desde início do report); release zerado |
| L4 | Cinco ciclos isolados confirmados. Janela `1794877750.2864249`–`1794877787.5008373`: somente dois reports periódicos `03`; nenhum report `20` ou outro sinal de botão |
| R4 | Cinco ciclos isolados confirmados. Janela `1794877787.5008533`–`1794877817.3490417`: somente um report periódico `03`; nenhum report `20` ou outro sinal de botão |

Na referência inicial há um ciclo A, um B e um Share. O usuário pediu repetição
da sequência inicial, por isso não se afirma que houve três ciclos por botão
nessa primeira parte USB. A referência final A/B/Share foi confirmada pelo
usuário, mas a janela de captura terminou depois de A; B/Share dessa referência
final não estão no arquivo. A comparação positiva usa os ciclos da parte inicial.

Conclusão limitada ao estado observado: L4/R4 não geraram sinais no endpoint de
entrada de jogo `0x82`, enquanto A/B/Share geraram. Assim, não há evidência de
que apenas adicionar códigos de paddle no evdev resolveria essa coleta. A
captura passiva não consulta endpoints sem URBs submetidas pelo host e não
prova ausência de um protocolo alternativo ou de emissão após inicialização
proprietária.

## Driver e Deadband

O código instalado `/usr/src/xone-0.5.8/driver/gamepad.c` habilita paddles para
identidades Microsoft Elite; não oferece esse tratamento para o G7 SE.
Entretanto a captura acima não contém um report de L4/R4 para esse caminho
decodificar. O decoder enhanced `0x12` do Deadband é de outra família/canal;
nenhum report `0x12` foi observado aqui.

A documentação `docs/g7se.md` do Deadband no commit já registrado limita
configuração aos descritores 6.30 e 6.64; outros são input-only. Seu probe
também valida a identidade/descritor antes de iniciar. Essa proteção não foi
alterada para forçar o layout 6.30 sobre o descritor 6.38.

## Interface de diagnóstico, leitura IN sem comando proprietário

`tools/probe_bulk_readonly.py` usou `ProbeHandle` do checkout Deadband
`/tmp/gamesr-deadband` no commit `3de56e8945ec1f99f4a4b7553af89564b3bb88bd`.
Verificou identidade exata e ausência de driver na interface 2, leu o alternate
setting original via GET_INTERFACE, selecionou alternate 1 e tentou bulk IN
`0x81`. Não chamou `write()`, não enviou pedidos vendor OUT e não modificou
perfis/firmware. SET_INTERFACE é uma alteração temporária de estado USB.

Resultado: quatro timeouts, depois `LIBUSB_ERROR_IO`, zero pacotes.
Não houve janela utilizável para um novo ensaio físico por essa interface.
`bulk-readonly.jsonl` registra restore do alternate 0 com resultado 0,
release com resultado 0 e driver da interface principal inalterado. Conferência
posterior confirmou o controle ainda conectado e `xone-wired` associado.

## Troca de modo e repetição após reinício

O manual oficial online descreve Xbox + Share para troca de modo. Foi solicitada
a combinação física, com observação de identidade USB em
`mode-switch-watch.jsonl`. O usuário percebeu apenas um reinício, consistente
com o log: desconexão, descritor transitório 0101 no endereço 5, nova desconexão
e retorno a 3537:1010/0638 no endereço 6, com xone-wired. Não foi observado
um modo alternativo estável. Não se interpreta 0101 como firmware instalado.

Feita nova captura USB passiva (`usbmon-post-restart.pcapng`) junto com evtest
(`evtest-post-restart.txt`). Usuário confirmou A uma vez, B uma vez, L4 cinco
vezes, R4 cinco vezes e Share uma vez, com pausas entre os grupos.
`usbmon-post-restart-payloads.tsv` e `usbmon-post-restart-decoded.json` mostram
um press/release de A (report offset 4 = 10), B (offset 4 = 20) e Share
(offset 18 = 01), com payloads zerados na soltura, e reports periódicos 03.
Nenhum report adicional dos traseiros. Evtest registra apenas os três pares
304/305/167, mantendo a mesma identidade e capacidades.

Resultado: captura independente de L4/R4 continua não demonstrada após esse
reinício. Não foram associados a F9/F10. A limitação não prova impossibilidade
em todos os firmwares ou protocolos proprietários.

Referências:

- https://gamesir.com/support/manuals/gamesir-g7-se
- https://github.com/broroeror/gamesir-linux-tools/blob/3de56e8945ec1f99f4a4b7553af89564b3bb88bd/docs/g7se.md
