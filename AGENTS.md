# Instruções do projeto

## Especificação e estado

- Spec principal: `specs/001-habilitar-l4-r4-share.md` (Spec 001).
- Evidências e limitações: `evidence/001/README.md` e
  `evidence/001/review/README.md`.
- L4/R4 ainda não têm captura independente comprovada no G7 SE observado
  (`3537:1010`, descritor USB `6.38`, modo GIP). Não tratar a entrega como completa.
- Não associar L4/R4 a A/B ou inventar códigos de origem para satisfazer testes.

## Comandos confirmados

Na raiz do projeto, com Python e `evdev` disponíveis:

```sh
python -m unittest tools.test_map_buttons -v
python tools/map_buttons.py --seconds 180
```

O primeiro comando executa nove testes de software. O segundo exige leitura do
dispositivo `/dev/input/event*` e escrita em `/dev/uinput`, e emite teclas reais.
A configuração é `config/mapping.json`; não executar instâncias concorrentes.

Na coleta física já realizada, foi usado evtest compilado localmente:

```sh
timeout 150s stdbuf -oL /tmp/gamesr-evtest /dev/input/event27
sudo timeout 150s stdbuf -oL /tmp/gamesr-evtest /dev/input/event28
```

Esses caminhos são exemplos da sessão validada, não dependências persistentes.
Localizar os nós atuais do controle e do teclado virtual antes de repetir.
O binário `/tmp/gamesr-evtest` não acompanha o repositório. Pode-se usar o evtest
instalado no sistema. Não capturar teclados pessoais para observar o uinput.

## Validação física obrigatória

- L4, R4 e Share exigem teste físico independente de press/release, comparado
  com A e B. Mostrar o comando e a sequência ao usuário antes de coletar.
- Testes unitários, mocks e replay de logs não aprovam captura física nem CA-01.
- Registrar VID:PID, descritor USB, modo quando conhecido, eventos por botão,
  versão do código e resultado de cada critério aplicável da spec.
- Somente mapear uma origem após comprovar que é distinta no hardware.
- Se ausente ou ambígua, investigar o caminho do Deadband para a identidade
  observada; registrar a limitação e manter o critério funcional pendente.
- Para origens válidas, acompanhar até a saída real uinput e verificar Share,
  A/B, reconexão, teclas presas e duplicidade no Steam conforme a spec.
- Encerrar processos temporários e restaurar alterações de configuração feitas
  para teste. Não alterar firmware ou perfis embarcados neste escopo.

## Publicação

- Revisar o conteúdo staged antes de qualquer commit/push.
- Não publicar credenciais, configurações pessoais, PCAPs, metadados de capturas
  do Steam ou logs brutos com identificadores locais. Respeitar `.gitignore`.
- O fixture `evidence/001/evtest-post-restart.txt` é uma exceção revisada:
  contém eventos do controle sem serial USB ou caminhos pessoais e é usado
  pelo teste de regressão. Não substituí-lo silenciosamente por outra coleta.
- Relatórios publicados referenciam arquivos brutos mantidos somente localmente;
  não apresentar esses links como downloads disponíveis no repositório.
- Preservar histórico remoto. Não fazer force-push.

## Revisão de specs

Após cada entrega validável ou bloqueio confirmado, delegue a revisão
ao `spec_editor`. Passe o caminho da spec, o diff e as evidências.
Aguarde o parecer antes de considerar a entrega concluída. Retome a
implementação dos itens em aberto quando houver um próximo passo
executável. Enquanto o revisor estiver ativo, deixe a edição da spec
com ele.
