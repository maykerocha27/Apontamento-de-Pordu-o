# Apontamento de Produção

Painel web local para a líder apontar o início e o término de cada Ordem de Produção
com apenas um clique em cada ponta. Faz parte dos painéis internos da Kit Lanche
Express (mesmo padrão do Painel de Solicitações de Compra e do Roteiro PCP).

## Como usar

1. Baixe os 3 arquivos deste repositório para uma pasta no computador (ex: via
   **Code → Download ZIP** aqui no GitHub, ou `git clone`).
2. Dê dois cliques em `iniciar_apontamento.bat`.
3. Uma janela preta abre o servidor e o navegador abre a página sozinho em
   `http://localhost:8766`.
4. Deixe a janela preta aberta enquanto a equipe estiver usando. Pra encerrar,
   feche a janela ou `Ctrl+C`.

Requer Python 3 instalado (com `py` no PATH) e o pacote `openpyxl`:

```
py -m pip install openpyxl
```

## Como funciona

- A líder digita (ou escolhe de uma sugestão já usada antes) o nome da **Ordem de
  Produção** e clica **Iniciar** — grava o checkpoint de início (dia e horário).
- Quando a ordem termina, ela acha a ordem na lista **Em andamento** e clica
  **Finalizar** — grava o checkpoint de término. Depois de finalizado não dá mais
  pra alterar.
- O **Histórico** embaixo mostra todas as ordens, com dia/hora de início e
  término, líder de cada ponta, duração e status.
- Tudo é gravado automaticamente em `apontamento_producao.xlsx`, criado na mesma
  pasta na primeira vez que o servidor roda.

## Arquivos

| Arquivo                     | O que é                                                  |
|------------------------------|-----------------------------------------------------------|
| `servidor_apontamento.py`   | Servidor local (Python puro, sem framework) + a API JSON  |
| `apontamento.html`          | A página que a líder usa                                  |
| `iniciar_apontamento.bat`   | Atalho: dois cliques e já abre tudo                        |

## Múltiplos computadores / mesma equipe

Cada computador que rodar `iniciar_apontamento.bat` cria/usa sua **própria**
planilha `apontamento_producao.xlsx`, na pasta local. Se mais de uma pessoa for
usar o painel e todas precisarem ver o mesmo histórico, a pasta do projeto
(com os 3 arquivos) precisa estar num lugar compartilhado entre elas, como uma
pasta do OneDrive sincronizada em ambos os computadores — assim a planilha fica
uma só, para todo mundo que abrir o `.bat`.

Se for necessário acessar de outro computador *pela rede* (sem OneDrive
compartilhado), é preciso liberar a porta 8766 no firewall do Windows do
computador que está rodando o servidor — nesse caso só um computador roda o
`iniciar_apontamento.bat`, e os demais acessam pelo navegador usando o IP dele
na rede local (o próprio servidor mostra esse endereço ao abrir).
