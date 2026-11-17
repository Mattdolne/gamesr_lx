# Revisão da spec 001 — 16/11/2026

## Resultado e localização da falha

L4/R4 estão bloqueados na captura de entrada. Não existe evento distinto
comprovado para encaminhar ao mapeamento ou ao uinput nesta unidade/modo.
Isso não demonstra defeito mecânico: o motivo de o dispositivo não transmitir
esses botões (perfil, firmware ou protocolo não ativado) não foi isolado.
CA-01 permanece **parcial**, sem aprovação global dos três botões.

| Botão | Captura física atual no evtest | Mapeamento | Saída uinput atual |
|---|---|---|---|
| A | 3 pares BTN_SOUTH / 304, valores 1/0 | Não associado | Nenhuma tecla emitida |
| B | 3 pares BTN_EAST / 305, valores 1/0 | Não associado | Nenhuma tecla emitida |
| L4 | Nenhum evento no grupo informado, 3 ciclos confirmados | Recusado sem origem independente | Sem F9 |
| R4 | Nenhum evento no grupo informado, 3 ciclos confirmados | Recusado sem origem independente | Sem F10 |
| Share sozinho | 4 pares KEY_RECORD / 167, valores 1/0 | KEY_RECORD → KEY_F11, modo tap | Exatamente 4 pares KEY_F11 / 87, valores 1/0 |

O usuário confirmou a sequência completa e, separadamente, que fez um quarto
toque de Share alguns segundos depois dos três primeiros. A contagem de quatro
neste log é uma entrada física adicional confirmada, não duplicação do programa.

Identidade atual: USB `3537:1010`, `bcdDevice=0638`, modo GIP, driver
`xone-wired`, bus 1/endereço 6, entrada `event27`. A versão evdev `0102`
é diferente do descritor USB e não foi usada como versão de firmware.

Fontes: [evtest-source.txt](evtest-source.txt), [evtest-uinput.txt](evtest-uinput.txt),
[mapper.txt](mapper.txt), [events.json](events.json).

Cada pressão Share foi correlacionada por timestamp a um press F11 seguido
de release. Latências observadas: 0,105 ms, 0,064 ms, 0,073 ms e 0,071 ms.
Nenhum par F9/F10 foi emitido e não houve pares F11 fora dos quatro toques.

## Deadband e evidência USB anterior revisados

Checkout consultado: `3de56e8945ec1f99f4a4b7553af89564b3bb88bd`.
O decoder `vendors/gamesir/models/g7se/input.py` lê o report GIP `0x20`
convencional, sem origens L4/R4. O `protocol.py` reconhece layouts de
configuração 6.30 e 6.64, rejeitando 6.38. O parser enhanced `0x12` de outros
modelos não é evidência de suporte ao G7 SE observado.

Foram revisados os PCAPs/TSVs e intervalos isolados da
[investigação USB](../usb-investigation.md): cinco ciclos de L4 e cinco de R4
confirmados, sem reports de entrada; A/B/Share com reports distintos. A leitura
bulk de diagnóstico anterior falhou sem dados e restaurou seu estado.
Não foi repetida nem forçada inicialização de firmware não suportado.
Não há captura distinta já disponível para implementar no mapper.

## Correção de código e diff

Não há repositório Git utilizável neste diretório; não foi possível revisar
diff contra HEAD/index. Antes da edição foram salvos os arquivos da rodada
em `/tmp/gamesr-review-001`. Os diffs locais antes/depois estão em
[map_buttons.diff](map_buttons.diff) e [tests.diff](tests.diff).

Defeito corrigido em `find_device()`: antes, a descoberta publicava `device`
antes de `active_keys()` terminar; uma desconexão nessa leitura deixava uma
referência inválida e o candidato sem fechamento no caminho de exceção.
Agora a seleção só retorna após ler identidade, capacidades e estado, fecha o
candidato que falhou e continua buscando outro dispositivo. Não se apresenta
essa correção de robustez como solução da ausência de L4/R4.

Mantida a recusa de fontes traseiras sem evidência. Associar L4 a BTN_SOUTH
ou R4 a BTN_EAST faria A/B acionarem teclas mapeadas e violaria CA-01.
O código não cria origens fictícias para satisfazer a configuração.

## Testes

`python -m unittest tools.test_map_buttons -v`: **9 testes passaram**.

- Configuração Share/KEY_RECORD → F11.
- Recusa de aliases L4→A e R4→B e de traseiros sem origem.
- Replay de entrada física gravada: A/B não emitem; Share emite um par F11.
- Desconexão durante a seleção: fecha candidato e usa o próximo com estado válido.
- Tap: ignora repeat e press duplicado; sem release extra no cleanup.
- Hold: libera uma só vez e permite próxima pressão.
- A/B não acionam o estado de emissão.

O replay e os mocks são testes de software, não novas provas de L4/R4 no
hardware. A nova rodada física acima comprovou entrada convencional e Share
até a saída real uinput após a correção. Não foi repetido o teste Steam nesta
rodada; permanece a evidência anterior de três capturas para três toques em tap.

## Comandos e sequência executados

```sh
timeout 150s stdbuf -oL /tmp/gamesr-evtest /dev/input/event27
python tools/map_buttons.py --seconds 180
sudo timeout 150s stdbuf -oL /tmp/gamesr-evtest /dev/input/event28
```

Primeiro iniciado o mapeador, depois os dois observadores em paralelo.
Sequência: A, B, L4, R4 e Share sozinho, três ciclos por grupo, pausas de três
segundos; usuário confirmou o quarto toque adicional de Share. O evtest foi
compilado anteriormente do fonte oficial, preservado em `../evtest.c`.
Os processos terminaram por seus limites de tempo. Nenhum serviço permanente,
perfil embarcado ou firmware foi alterado nesta revisão.

Conclusão: captura L4/R4 ainda sem correção funcional demonstrável. Mapeamento
e emissão de Share passam; A/B não regrediram no evtest nem acionam F11.
