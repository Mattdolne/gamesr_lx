# GameSir G7 SE no Linux

Diagnóstico e mapeamento local de botões do GameSir G7 SE via evdev/uinput,
conforme a [Spec 001](specs/001-habilitar-l4-r4-share.md).

Estado: Share tem captura independente comprovada e mapeamento configurável.
L4/R4 continuam sem origem independente no hardware/modo observado; não estão
habilitados pelo programa. A entrega da spec permanece parcial.

## Execução e testes

Dependência validada: Python com `evdev==2.0.0` (ver `requirements.txt`).

```sh
python -m unittest tools.test_map_buttons -v
python tools/map_buttons.py
```

O mapeador requer leitura do controle em `/dev/input` e escrita em `/dev/uinput`.
A configuração salva em [mapping.json](config/mapping.json) usa Share→F11 em
modo `tap`: um par curto press/release por pressão física. O modo `hold` mantém
a tecla até soltar o botão e pode repetir ações conforme o aplicativo consumidor.
Use Ctrl+C para encerrar. Não foi instalado serviço de inicialização automática.

Os nove testes cobrem configuração, recusa de origens ambíguas, replay de eventos,
estado das teclas e seleção do dispositivo. Testes de software não substituem
a validação física exigida em [AGENTS.md](AGENTS.md).

## Evidências

Ver [resultados](evidence/001/README.md), [investigação USB](evidence/001/usb-investigation.md)
e [revisão](evidence/001/review/README.md). Os relatórios foram preservados como
registro da sessão: links para PCAPs, logs auxiliares e metadados referem-se a
artefatos locais excluídos da publicação. O log evtest usado pelo teste de replay
é o único fixture bruto publicado e foi revisado para não conter identificadores
pessoais.

`tools/probe_bulk_readonly.py` é uma ferramenta experimental de diagnóstico;
depende de checkout separado do Deadband informado por `--deadband`, não incluído
aqui. Não é necessária para os testes nem para executar o mapeador.
