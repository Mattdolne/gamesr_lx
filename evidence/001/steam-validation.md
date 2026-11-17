# Validação Steam / Skyrim Special Edition

- Jogo: The Elder Scrolls V: Skyrim Special Edition, app 489830.
- Steam Input desabilitado, conforme imagem do usuário: compatibilidade nativa.
- Tela de atribuição do Skyrim aceita apenas botões convencionais do controle;
  usuário confirmou que não aceita teclado físico, L4/R4 ou Share.
- Por isso, teste inicial de ação associada dentro do jogo ficou bloqueado.

## Ação local observável: captura do Steam

A spec define a ação local como tecla configurável, não exige ação de gameplay.
Foi usado o atalho de captura do próprio Steam para observar F11 com o jogo em
execução, preservando o escopo de teclado uinput.

Usuário alterou temporariamente o atalho de captura de F12 para F11 em
Steam → Configurações → Em jogo. Referência:
https://partner.steamgames.com/doc/features/screenshots?language=english

Sem mapeador, usuário confirmou: F11 físico tira captura, Share sozinho não.
A preparação produziu dois arquivos de captura; não se atribui individualmente
cada arquivo a um toque com base apenas no horário de gravação. A contagem
imediatamente antes de iniciar o mapeador foi dois (`steam-before-mapper.json`).

Metadados das capturas, sem abrir ou copiar imagens do jogo, foram observados
em `steam-screenshot-watch.jsonl`. Não houve envio das imagens para serviço externo.

## Rodada com Share → F11

Foi iniciado um único mapeador lendo `config/mapping.json`, com limite de 300 s.
Log `mapper-steam-screenshots.txt`; saída uinput observada separadamente em
`uinput-steam-screenshots.txt` via evtest.

Solicitado: três toques de Share separados por três segundos, sem F11 físico;
depois A/B e inspeção de segundo comando inesperado.

Usuário relatou três capturas, A/B normais e nenhum segundo comando. Porém os
metadados mostraram quatro novos arquivos (contagem 2→6), enquanto o evtest e o
mapeador registraram três pares F11. No primeiro toque, F11 ficou pressionado
de `1794878376.238568` a `1794878376.910552` (~672 ms). Foram criadas imagens
em `1794878376.3237092` e `1794878376.903719`, ambas durante esse toque.
As outras pressões criaram uma imagem cada. Portanto a rodada hold não passa
a verificação de uma captura por pressão. A captura extra é compatível com
repetição do atalho na camada gráfica/Steam, mas a origem exata da repetição
não foi isolada.

## Ajuste e nova rodada

Adicionado `output_mode` configurável: `hold` mantém a tecla até soltar o botão;
`tap` emite press/release imediatamente na borda de pressão e ignora repeats,
press duplicado e a soltura física até a próxima pressão distinta. Configuração
atual: `output_mode: tap`, Share→F11. Isso evita manter F11 segurado para a ação
de captura. O modo hold continua disponível, inclusive para uso que exija tecla
segurada, mas pode repetir ações conforme o consumidor.

Quatro testes de estado passaram (`python -m unittest tools.test_map_buttons -v`):
deduplicação/repeat em tap; cleanup de tap sem release extra; liberação de hold
uma só vez com nova pressão depois; A/B ignorados.

Contagem antes da rodada tap: seis arquivos (`steam-before-tap.json`).
Solicitado um toque curto, um de 1 s e um de 3 s, separados por pausas.
Entrada física em `evtest-steam-tap-source.txt`, saída em
`uinput-steam-tap.txt`, mapeador em `mapper-steam-tap.txt`.
Resultado: aprovado para Share como ação de captura do Steam durante Skyrim.
`steam-after-tap.json` contém nove arquivos, contra seis antes da rodada:
exatamente três novos arquivos. Nenhuma imagem foi aberta para a contagem.
Usuário confirmou três capturas, A/B normais e nenhum segundo comando.

Durações físicas observadas no evtest: aproximadamente 0,088 s, 0,440 s e
2,116 s. As durações de 1 s e 3 s eram instruções, não medidas; a evidência
usa os valores reais. Os três pares de saída F11 duraram aproximadamente
0,480 ms, 0,040 ms e 0,036 ms. A pressão física de ~2,1 s não gerou repetição.
Nenhum novo par F11 foi emitido quando A/B foram usados na mesma rodada.

CA-04 passa para Share, para essa ação e estado do Steam Input. L4/R4 continuam
pendentes porque não foram capturados de forma independente. Não foi testado
com Steam Input habilitado.

Usuário confirmou restauração do atalho de F11 para o valor original F12.
Configuração do mapeador permanece Share→F11/tap,
com execução temporária encerrada ao final do teste.

Essa abordagem pode validar uma ação do Steam durante o jogo; ela não demonstra
que o Skyrim aceita teclado e controle simultaneamente para ações de gameplay.
