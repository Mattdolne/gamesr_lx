# Spec 001 — Habilitar L4, R4 e Share no GameSir G7 SE

**Status:** entrega parcial; L4/R4 bloqueados na captura de entrada na unidade
`3537:1010`, descritor USB `6.38`, modo GIP. A ausência de eventos no evtest e
de relatórios de entrada na captura USB passiva não demonstra defeito mecânico
nem impossibilidade em todos os modos ou firmwares. Share foi distinguido de
A/B e acompanhado até a saída real uinput nas coletas registradas.

Revisão documental em 16/11/2026: código/configuração do commit base `9aeef78`,
diff atual, diffs locais da correção de seleção do dispositivo, nove testes
de software aprovados e logs já existentes. **Não houve nova coleta física
nesta revisão documental.** Ver [evidências](../evidence/001/README.md),
[revisão de código e coleta física anterior](../evidence/001/review/README.md)
e o acompanhamento por critério abaixo. Nenhum critério funcional dos três
botões está aprovado globalmente.

## Objetivo

No CachyOS, com o G7 SE conectado via USB, atribuir e executar uma ação local independente para cada um dos três botões: L4, R4 e Share.

## Escopo

Nesta entrega, uma ação local equivale a uma tecla configurável. F9, F10 e F11 são os valores usados na validação. A configuração é salva no Linux e aplicada enquanto o programa estiver em execução.

Ficam fora desta entrega a interface gráfica, a gravação de perfis no controle, a atualização de firmware e a exposição de botões extras como parte de um gamepad virtual.

## Critérios de aceite

| ID | Cenário | Resultado esperado |
|---|---|---|
| CA-01 | Configurar L4 → F9, R4 → F10 e Share → F11. Pressionar e soltar cada botão isoladamente. | Cada botão emite apenas o pressionamento e a soltura da tecla atribuída. Pressionar A ou B isoladamente não aciona F9, F10 ou F11. |
| CA-02 | Trocar a tecla atribuída a um botão, salvar e reiniciar o programa. | O novo mapeamento é recuperado e aplicado. Os outros dois mantêm suas atribuições. |
| CA-03 | Desconectar o controle segurando um botão mapeado e reconectá-lo. | A tecla emitida é liberada. Após reconectar, os mapeamentos funcionam novamente sem reiniciar o programa. |
| CA-04 | Testar o controle em um jogo no Steam com os mapeamentos ativos. | Os botões convencionais continuam funcionando. Cada botão mapeado gera a ação configurada sem um segundo comando no jogo para a mesma pressão. |
| CA-05 | Conectar uma unidade ou usar um modo em que algum dos três botões não possa ser distinguido. | O programa identifica o botão afetado, informa a limitação e inclui a identidade USB e o modo quando conhecido. Uma entrada ambígua não é usada como origem de mapeamento. O critério funcional do botão permanece pendente. |

## Acompanhamento por critério — 16/11/2026

Os estados abaixo se referem ao critério inteiro. Uma verificação de Share
não aprova automaticamente L4/R4. Os arquivos brutos citados pelos relatórios
são artefatos locais não publicados; os relatórios e o fixture de replay
revisado permanecem no repositório.

| ID | Estado | Comprovado e evidência | Trabalho ou teste faltante |
|---|---|---|---|
| CA-01 | **Parcial** | Na coleta física da [revisão](../evidence/001/review/README.md), A/B produziram três pares `BTN_SOUTH`/`BTN_EAST`; Share sozinho produziu quatro pares `KEY_RECORD` e exatamente quatro pares F11 no uinput. O usuário confirmou o quarto toque adicional. A/B não emitiram teclas mapeadas. | Captura independente de L4 e R4 está **bloqueada** no estado observado. Sem origens distintas, não configurar F9/F10. Após obter captura válida, acompanhar cada origem até press/release no uinput e repetir a comparação com A/B. Ver também a proposta sobre `tap`/`hold` abaixo. |
| CA-02 | **Parcial** | A [evidência de persistência](../evidence/001/README.md) registra Share alterado para F10, arquivo salvo, processo reiniciado e um par F10 real sincronizado a Share; A/B não emitiram teclas. Depois foi restaurado F11. | Validar alteração e persistência para L4/R4 quando capturados, incluindo manutenção das outras duas atribuições. Não foi possível comprovar preservação de três mapeamentos independentes com somente Share disponível. |
| CA-03 | **Parcial** | Na [coleta de reconexão](../evidence/001/README.md), o controle enviou release antes de desaparecer; F11 ficou liberado, houve redescoberta sem reinício e novos pares após reconectar. O botão segurado na reconexão foi detectado (`blocked=[167]`). | O ramo de limpeza com tecla ainda mantida internamente foi testado em software, não exercitado fisicamente nessa desconexão. Repetir o cenário aplicável para L4/R4 quando houver captura. A correção de `find_device()` tem teste com mock; desconexão/reconexão posterior no log atual, sem novo toque confirmado, não amplia a aprovação física. |
| CA-04 | **Parcial** | Na [validação Steam](../evidence/001/steam-validation.md), Share→F11 em `tap` gerou três capturas novas para três pressões, incluindo uma de aproximadamente 2,1 s, durante Skyrim Special Edition, Steam Input desabilitado. Usuário confirmou A/B normais e nenhum segundo comando. | Validar L4/R4 após captura. A rodada `hold` produziu quatro capturas para três pressões e não passa para essa ação. O resultado verificado é captura do Steam durante o jogo; a tela do Skyrim recusou teclado, portanto não há prova de ação de gameplay por F11 nem de outros estados do Steam Input. |
| CA-05 | **Verificado na unidade/modo observado** | O [diagnóstico registrado](../evidence/001/review/README.md) informa L4/R4 sem captura independente, `3537:1010` e GIP; o programa não os usa como origem. Os testes recusam alias L4→A/R4→B e mapeamento sem fonte validada. A [investigação USB/Deadband](../evidence/001/usb-investigation.md) não encontrou leitura distinta para `6.38`. | Manter os critérios funcionais de L4/R4 pendentes. Qualquer outra identidade/modo precisa de sua própria identificação e coleta; não generalizar essa verificação para hardware não testado. |

### Testes de software e limites dos logs

`python -m unittest tools.test_map_buttons -v` teve nove testes aprovados na
rodada de revisão: configuração Share, recusa de fontes traseiras ambíguas ou
ausentes, replay do fixture físico, seleção após falha de leitura inicial,
deduplicação/repeat, liberação de teclas e não acionamento por A/B. Replay e
mocks verificam lógica de software; não substituem pressões no hardware.

O log local `evidence/001/review/evtest-source.txt` tem sufixo inválido após a
coleta útil, com timestamps/códigos impossíveis e core dump. Somente o prefixo
válido correspondente aos eventos de `review/events.json`, confrontado com
`review/evtest-uinput.txt`, sustenta os quatro ciclos de Share e os grupos A/B.
Não contar o release repetido junto da corrupção como nova pressão, nem usar
o sufixo para atribuir botões ou concluir ausência/presença de novos eventos.
`review/mapper.txt` registra desconexão/reconexão posterior; isso, isoladamente,
não comprova nova ação física após reconectar.

### Comportamento implementado e proposta pendente

O código já oferece `output_mode: hold` (release na soltura física) e `tap`
(press/release curto na borda de pressão, mesmo mantendo o botão). O arquivo
atual usa `tap` para Share→F11. Esse comportamento foi observado nos testes;
não se altera aqui o texto normativo de CA-01 nem se assume decisão explícita
do usuário sobre duração da tecla ou modo padrão.

**Proposta P-01, pendente de decisão:** explicitar se CA-01 admite os dois modos
e qual deve ser o padrão. Motivo: `tap` evitou repetição de capturas ao segurar
Share, mas não mantém a tecla pressionada; `hold` preserva a duração física e
pode repetir ações conforme o consumidor. A decisão deve orientar os testes
de duração e reconexão, sem remover a exigência de fontes independentes.

Captura do Steam é uma ação local observável de F11 no escopo atual. Não se
propõe ampliar essa evidência para gameplay: se esse passar a ser um requisito,
será necessária decisão de escopo e validação própria no jogo que aceite a
combinação de teclado e controle.

## Diagnóstico inicial

1. Conectar o controle por USB e habilitar as travas traseiras para uso de L4 e R4. Registrar VID:PID com `lsusb` e o modo e firmware, quando identificáveis.
2. Comparar no `evtest` os eventos de pressionamento e soltura de L4, R4, Share, A e B. Testar Share sozinho.
3. Se um botão estiver ausente ou produzir eventos indistinguíveis dos de outro botão, verificar como o Deadband lê os botões extras na identidade USB observada. Confirmar a distinção no hardware antes de associar o botão a uma tecla.
4. Com a captura validada, implementar a emissão das teclas via `uinput` e executar os cenários de aceite.

## Evidência para concluir

Anexar à issue o VID:PID, o modo quando conhecido, os eventos observados por botão e o resultado de cada critério de aceite. Registrar o jogo usado e o estado do Steam Input no teste de duplicidade. Considerar a entrega concluída quando os três botões passarem pelos testes físicos aplicáveis.

## Referências

- [Manual do GameSir G7 SE](https://gamesir.com/support/manuals/gamesir-g7-se)
- [Deadband](https://github.com/broroeror/gamesir-linux-tools)
- [Documentação do uinput](https://docs.kernel.org/input/uinput.html)
