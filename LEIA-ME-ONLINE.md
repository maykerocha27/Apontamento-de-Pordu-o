# Apontamento de Produção online — Supabase + GitHub Pages

Esse é o caminho sem servidor: o banco de dados fica no Supabase (grátis) e a
página fica hospedada de graça no próprio GitHub (GitHub Pages), num link fixo
tipo `https://maykerocha27.github.io/Apontamento-de-Pordu-o/`. Ninguém precisa
rodar nada local.

> Isso substitui os arquivos `servidor_apontamento.py`, `app.py` e o caminho
> pelo PythonAnywhere — pode ignorar aqueles a partir de agora.

## 1. Criar o projeto no Supabase

1. Vá em **supabase.com** → **Start your project** → crie a conta (dá pra
   entrar com GitHub, usando a mesma conta `maykerocha27`).
2. **New project** → escolha um nome (ex: `apontamento-kle`), uma senha pro
   banco (guarde essa senha num lugar seguro — não precisa dela de novo nesse
   processo, é só backup) e a região mais próxima (ex: South America).
3. Espera uns 2 minutos o projeto terminar de subir.

## 2. Criar a tabela

1. No projeto, abre **SQL Editor** (menu da esquerda) → **New query**.
2. Abre o arquivo `supabase_setup.sql` que te mandei, copia todo o conteúdo e
   cola ali.
3. Clica em **Run**. Deve aparecer "Success. No rows returned".

## 3. Pegar a URL e a chave do projeto

1. Menu da esquerda → **Project Settings** (ícone de engrenagem) → **API**.
2. Copia o valor de **Project URL** (algo como `https://xxxxxxx.supabase.co`).
3. Copia o valor de **anon public** (uma chave longa, em "Project API keys").
   Essa chave é feita pra ficar pública numa página web — não é segredo.

## 4. Configurar a página

1. Abre o `index.html` que te mandei (no editor de texto, ou direto no GitHub
   pelo lápis depois de subir).
2. Troca essas 3 linhas, perto do topo do `<script>`:
   ```js
   var SUPABASE_URL = "COLE_AQUI_A_PROJECT_URL";
   var SUPABASE_ANON_KEY = "COLE_AQUI_A_ANON_KEY";
   var SENHA_PAINEL = "troque-esta-senha";
   ```
   pela URL e chave do passo 3, e por uma senha sua pra equipe entrar no
   painel.

## 5. Subir pro GitHub

No repositório `github.com/maykerocha27/Apontamento-de-Pordu-o`:
**Add file → Upload files** → arrasta o `index.html` já editado →
**Commit changes**.

## 6. Ligar o GitHub Pages

1. No repositório, aba **Settings** → **Pages** (menu da esquerda).
2. Em **Source**, escolha **Deploy from a branch**.
3. Em **Branch**, escolha `main` e a pasta `/ (root)` → **Save**.
4. Espera 1-2 minutos. Atualiza a página — vai aparecer um link verde tipo
   `https://maykerocha27.github.io/Apontamento-de-Pordu-o/`. É esse o link
   pra você e pra líder usarem, de qualquer computador ou celular.

## Importante sobre a senha

Essa senha é um filtro simples pra impedir que alguém de fora, achando o
link por acaso, entre direto no painel — ela não é uma segurança forte tipo
banco. Como é uma página pública (GitHub Pages é sempre público), qualquer
pessoa que souber mexer em "ver código-fonte" do navegador consegue achar
essa senha. Pra um painel interno só com horários de produção (sem dado
sensível), isso é suficiente — só não trate como se fosse proteger algo
confidencial.

## Se quiser atualizar a página depois

Repete os passos 4 e 5: edita o `index.html`, sobe de novo no GitHub (mesmo
nome de arquivo substitui o antigo). O GitHub Pages atualiza sozinho em
1-2 minutos.

## Lembrete do Supabase

O projeto grátis do Supabase pausa depois de **1 semana sem uso**. Como a
líder vai mexer nisso todo dia útil, não deve pausar nunca — mas se algum dia
o painel parar de carregar dados, entra em **supabase.com** → o projeto → tem
um botão pra reativar, é de graça e na hora.
