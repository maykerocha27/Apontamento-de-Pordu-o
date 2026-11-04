"""
App WEB do Apontamento de Produção, para rodar online (PythonAnywhere ou
qualquer host que sirva um app WSGI). Usa a MESMA lógica de negócio de
servidor_apontamento.py (o mesmo que roda local via iniciar_apontamento.bat) --
só muda a "camada" que recebe as requisições: aqui é WSGI em vez de um
servidor HTTP próprio, porque é o formato que hosts gratuitos tipo
PythonAnywhere exigem.

Pede usuário e senha (a própria tela de login do navegador) antes de deixar
usar o painel, já que esse link fica na internet.

Veja LEIA-ME-DEPLOY.md para o passo a passo de colocar isso no ar.
"""
import base64
import json
import os
import sys

PASTA = os.path.dirname(os.path.abspath(__file__))
if PASTA not in sys.path:
    sys.path.insert(0, PASTA)

from servidor_apontamento import (
    ErroPlanilha, HTML, VERSAO,
    finalizar, iniciar, listar, ordens_sugeridas,
)

# ---------------------------------------------------------------------------
# TROQUE AQUI a senha antes de divulgar o link pra equipe.
USUARIO = "kle"
SENHA = "troque-esta-senha"
# ---------------------------------------------------------------------------


def _nao_autorizado(start_response):
    start_response("401 Unauthorized", [
        ("WWW-Authenticate", 'Basic realm="Apontamento de Producao"'),
        ("Content-Type", "text/plain; charset=utf-8"),
    ])
    return [b"Usuario ou senha incorretos."]


def _autorizado(environ):
    auth = environ.get("HTTP_AUTHORIZATION", "")
    if not auth.startswith("Basic "):
        return False
    try:
        decodificado = base64.b64decode(auth[6:]).decode("utf-8")
        usuario, _, senha = decodificado.partition(":")
    except Exception:
        return False
    return usuario == USUARIO and senha == SENHA


def _json(start_response, codigo, obj):
    corpo = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    textos = {200: "200 OK", 404: "404 Not Found", 423: "423 Locked", 500: "500 Internal Server Error"}
    start_response(textos.get(codigo, "%d Erro" % codigo), [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Content-Length", str(len(corpo))),
        ("Cache-Control", "no-store"),
    ])
    return [corpo]


def application(environ, start_response):
    if not _autorizado(environ):
        return _nao_autorizado(start_response)

    metodo = environ.get("REQUEST_METHOD", "GET")
    caminho = environ.get("PATH_INFO", "/")

    try:
        if metodo == "GET":
            if caminho == "/api/versao":
                return _json(start_response, 200, {"versao": VERSAO})
            if caminho == "/api/apontamentos":
                return _json(start_response, 200, listar())
            if caminho == "/api/ordens-sugeridas":
                return _json(start_response, 200, ordens_sugeridas())
            if caminho in ("/", "/index.html"):
                with open(HTML, "rb") as f:
                    dados = f.read()
                start_response("200 OK", [
                    ("Content-Type", "text/html; charset=utf-8"),
                    ("Content-Length", str(len(dados))),
                    ("Cache-Control", "no-store"),
                ])
                return [dados]
            return _json(start_response, 404, {"erro": "nao encontrado"})

        if metodo == "POST":
            tam = int(environ.get("CONTENT_LENGTH") or 0)
            corpo = environ["wsgi.input"].read(tam) if tam else b""
            dados = json.loads(corpo.decode("utf-8")) if corpo else {}

            if caminho == "/api/apontamentos/iniciar":
                item = iniciar(dados.get("ordem"), dados.get("lider"))
                return _json(start_response, 200, {"ok": True, "item": item})

            if caminho.startswith("/api/apontamentos/") and caminho.endswith("/finalizar"):
                rid = caminho.split("/")[3]
                item = finalizar(rid, dados.get("lider"))
                return _json(start_response, 200 if item else 404, {
                    "ok": bool(item), "item": item,
                    "erro": "" if item else "Ordem nao encontrada. Atualize a pagina.",
                })

            return _json(start_response, 404, {"erro": "nao encontrado"})

        return _json(start_response, 404, {"erro": "nao encontrado"})

    except ErroPlanilha as e:
        return _json(start_response, 423, {"erro": str(e)})
    except Exception as e:
        return _json(start_response, 500, {"erro": "Erro inesperado: %s" % e})


# Pra testar local antes de subir: py app.py  -> http://localhost:8000
if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    porta = int(os.getenv("PORT", "8000"))
    print("Teste local do app.py em http://localhost:%d  (usuario=%s senha=%s)" % (porta, USUARIO, SENHA))
    make_server("0.0.0.0", porta, application).serve_forever()
