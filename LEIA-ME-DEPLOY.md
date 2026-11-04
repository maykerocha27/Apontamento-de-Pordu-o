# Colocar o Apontamento de Produção online (link único pra todo mundo)

Isso coloca o painel num link fixo (tipo `https://seuusuario.pythonanywhere.com`)
que você e a líder acessam de qualquer computador, sem precisar rodar nada local.
Usa o PythonAnywhere, que tem plano grátis (sem cartão de crédito).

## 1. Trocar a senha antes de tudo

Abra o arquivo `app.py` aqui no GitHub (ícone do lápis, no canto superior
direito do arquivo) e troque a linha:

```python
SENHA = "troque-esta-senha"
```

por uma senha sua, tipo:

```python
SENHA = "kle2026producao"
```

Clique em **Commit changes** pra salvar. (O usuário fica fixo como `kle` — se
quiser mudar, é a linha `USUARIO = "kle"` logo acima.)

## 2. Criar a conta no PythonAnywhere

1. Vá em **pythonanywhere.com** → **Pricing & signup** → **Create a Beginner account** (grátis).
2. Confirme o e-mail.

## 3. Trazer o código do GitHub pra lá

1. No painel do PythonAnywhere, abra a aba **Consoles** → **Bash**.
2. Cole e rode:
   ```
   git clone https://github.com/maykerocha27/Apontamento-de-Pordu-o.git apontamento
   ```
3. Instale a dependência:
   ```
   pip3.10 install --user openpyxl
   ```
   (se o comando `pip3.10` não existir, rode `python3 --version` pra ver a
   versão exibida nas abas do PythonAnywhere e troque o número, ex: `pip3.11`)

## 4. Criar o site (Web app)

1. Aba **Web** → **Add a new web app** → avança a tela de boas-vindas.
2. Domínio grátis sugerido (algo como `seuusuario.pythonanywhere.com`) → **Next**.
3. Escolha **Manual configuration** (não escolha Flask/Django) → escolha a
   versão de Python mais recente da lista → **Next**.

## 5. Apontar o site pro nosso app.py

Ainda na aba **Web**, role até **Code**:

- **Source code**: `/home/SEUUSUARIO/apontamento` (troque `SEUUSUARIO` pelo seu
  usuário do PythonAnywhere)
- **Working directory**: mesma coisa, `/home/SEUUSUARIO/apontamento`
- Clique no link **WSGI configuration file** (abre um editor). Apague tudo o
  que estiver lá e cole só isto (trocando `SEUUSUARIO`):
  ```python
  import sys
  path = '/home/SEUUSUARIO/apontamento'
  if path not in sys.path:
      sys.path.insert(0, path)
  from app import application
  ```
  Clique em **Save**.

## 6. Colocar no ar

Volte pra aba **Web** e clique no botão verde **Reload**.

Pronto — o link `https://seuusuario.pythonanywhere.com` já está valendo. Ao
abrir, o navegador vai pedir usuário e senha (os que você definiu no passo 1).
Isso só é pedido uma vez por navegador.

## Atualizando depois (se eu mandar uma versão nova do código)

1. Suba os arquivos novos no GitHub (do jeito que já fizemos).
2. Aba **Consoles** → abra o console Bash que já existe (ou um novo) e rode:
   ```
   cd apontamento && git pull
   ```
3. Aba **Web** → **Reload**.

## Importante

- A planilha `apontamento_producao.xlsx` com o histórico passa a ser criada
  **lá no PythonAnywhere**, separada da que estava sendo usada localmente no
  seu computador (se já tinha testado algo por aí). É o arquivo que vale a
  partir de agora, com todo mundo usando o mesmo link.
- O plano grátis do PythonAnywhere tem limite de uso de CPU por dia, mas é bem
  folgado pra um painel de uso leve como esse (alguns cliques por dia).
- Se algum dia quiser baixar a planilha pra olhar no Excel: aba **Files** do
  PythonAnywhere → pasta `apontamento` → `apontamento_producao.xlsx` → ícone
  de download.
