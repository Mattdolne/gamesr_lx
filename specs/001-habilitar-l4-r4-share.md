# Spec 001 — Habilitar L4, R4 e Share no GameSir G7 SE

**Status:** validação física parcial em 16/11/2026. Share distinguido de A/B;
L4/R4 sem eventos no evtest nem relatórios de entrada na captura USB passiva,
inclusive após reinício por Xbox + Share. Share validado via uinput, alteração
persistente de tecla e reconexão. No Skyrim com Steam Input desabilitado,
Share→F11 em modo tap gerou uma captura do Steam por pressão, incluindo
pressão longa, sem duplicidade observada e com A/B normais. A tela de controles
do Skyrim não aceitou teclado; não foi validada ação de gameplay por F11.
Ver [evidências e resultados](../evidence/001/README.md).
Revisão de código e nova rodada física: [relatório](../evidence/001/review/README.md).
CA-01 permanece parcial: nenhuma captura distinta de L4/R4; Share→F11 e
ausência de acionamento por A/B foram reconfirmados após correção de seleção
do dispositivo.

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
