"""
Servidor do Apontamento de Produção.

A líder só clica: digita (ou escolhe de uma sugestão já usada antes) o nome
da Ordem de Produção e clica "Iniciar" -- isso grava o checkpoint de início
(dia e horário). Quando a ordem termina, ela acha a ordem na lista "Em
andamento" e clica "Finalizar" -- grava o checkpoint de término. Tudo fica
registrado embaixo, no Histórico (dia e horário de início/término de cada
ordem), gravado em apontamento_producao.xlsx (mesma pasta).

Como usar:  py servidor_apontamento.py     (ou dois cliques em iniciar_apontamento.bat)
Deixe a janela aberta enquanto a equipe estiver usando.

Opcional (.env ou variável de ambiente):
  APONTAMENTO_PORTA = 8766
"""

import json
import os
import socket
import sys
import threading
import unicodedata
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

PASTA = os.path.dirname(os.path.abspath(__file__))
XLSX = os.path.join(PASTA, "apontamento_producao.xlsx")
HTML = os.path.join(PASTA, "apontamento.html")
ABA = "Apontamentos"
VERSAO = 1  # a página confere este número para detectar servidor antigo ainda ligado
PORTA = int(os.getenv("APONTAMENTO_PORTA", "8766"))
TRAVA = threading.Lock()

# colunas: A ID | B Ordem | C Líder (início) | D Início | E Líder (término) | F Término | G Status
COLS = {"id": 1, "ordem": 2, "lider_inicio": 3, "inicio": 4, "lider_termino": 5, "termino": 6, "status": 7}
CABECALHO = ["ID", "Ordem de Produção", "Líder (início)", "Início", "Líder (término)", "Término", "Status"]
NCOL = len(CABECALHO)
LIMITE = 2000  # linhas preparadas (formatação)
FONTE = "Arial"
FMT_DATAHORA = "dd/mm/yyyy hh:mm"


class ErroPlanilha(Exception):
    pass


# ----------------------------------------------------------------------------- utilitários
def _txt(v):
    return "" if v is None else str(v).strip()


def _norm(s):
    s = unicodedata.normalize("NFKD", _txt(s)).encode("ascii", "ignore").decode("ascii")
    return " ".join(s.lower().split())


def _fmt_datahora(dt):
    if not isinstance(dt, datetime):
        return ""
    return dt.strftime("%d/%m/%Y %H:%M")


# ----------------------------------------------------------------------------- planilha
def _estilo_linha(ws, r):
    borda = Border(bottom=Side(style="thin", color="D0D5DA"))
    for col in range(1, NCOL + 1):
        c = ws.cell(row=r, column=col)
        c.font = Font(name=FONTE, size=10)
        c.border = borda
        if col in (4, 6, 7):
            c.alignment = Alignment(horizontal="center")
    ws.cell(row=r, column=COLS["inicio"]).number_format = FMT_DATAHORA
    ws.cell(row=r, column=COLS["termino"]).number_format = FMT_DATAHORA


def _montar_planilha():
    wb = Workbook()
    ws = wb.active
    ws.title = ABA
    ws.append(CABECALHO)
    for c in ws[1]:
        c.font = Font(name=FONTE, bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="1F3A5F")
        c.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 24
    for r in range(2, LIMITE + 1):
        _estilo_linha(ws, r)
    for col, w in zip("ABCDEFG", [12, 42, 20, 18, 20, 18, 14]):
        ws.column_dimensions[col].width = w
    ws.column_dimensions["A"].hidden = True
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:G{LIMITE}"
    lg = wb.create_sheet("Como usar")
    textos = ["Apontamento de Produção - como usar", "",
              "O cadastro é feito pela página do sistema (iniciar_apontamento.bat). Ela grava nesta planilha automaticamente.",
              "A líder digita o nome da Ordem de Produção e clica 'Iniciar' -- grava o checkpoint de início (dia e hora).",
              "Quando a ordem termina, a líder acha a ordem na lista 'Em andamento' e clica 'Finalizar' -- grava o checkpoint de término.",
              "O Histórico embaixo da página mostra todas as ordens, com dia/hora de início e término de cada uma.",
              "Evite editar esta planilha direto no Excel enquanto o servidor estiver em uso (o Excel trava o arquivo)."]
    for i, t in enumerate(textos, 1):
        lg[f"A{i}"] = t
        lg[f"A{i}"].font = Font(name=FONTE, bold=(i == 1), size=14 if i == 1 else 11)
    lg.column_dimensions["A"].width = 110
    return wb


def _abrir():
    try:
        if not os.path.exists(XLSX):
            _montar_planilha().save(XLSX)
        wb = load_workbook(XLSX)
        ws = wb[ABA] if ABA in wb.sheetnames else wb.active
        return wb, ws
    except PermissionError:
        raise ErroPlanilha("A planilha está aberta no Excel. Feche-a e tente de novo.")


def _salvar(wb):
    try:
        wb.save(XLSX)
    except PermissionError:
        raise ErroPlanilha("A planilha está aberta no Excel. Feche-a e tente de novo.")


def _linhas(ws):
    saida = []
    for r in range(2, ws.max_row + 1):
        ordem = _txt(ws.cell(row=r, column=COLS["ordem"]).value)
        if not ordem:
            continue
        inicio = ws.cell(row=r, column=COLS["inicio"]).value
        termino = ws.cell(row=r, column=COLS["termino"]).value
        saida.append({
            "id": _txt(ws.cell(row=r, column=COLS["id"]).value),
            "row": r,
            "ordem": ordem,
            "lider_inicio": _txt(ws.cell(row=r, column=COLS["lider_inicio"]).value),
            "inicio": inicio if isinstance(inicio, datetime) else None,
            "lider_termino": _txt(ws.cell(row=r, column=COLS["lider_termino"]).value),
            "termino": termino if isinstance(termino, datetime) else None,
        })
    return saida


def _primeira_linha_vazia(ws):
    r = 2
    while _txt(ws.cell(row=r, column=COLS["ordem"]).value):
        r += 1
    return r


def _saida(l):
    inicio, termino = l["inicio"], l["termino"]
    duracao_min = None
    if inicio and termino:
        duracao_min = max(0, round((termino - inicio).total_seconds() / 60))
    return {
        "id": l["id"],
        "ordem": l["ordem"],
        "lider_inicio": l["lider_inicio"],
        "inicio": _fmt_datahora(inicio),
        "lider_termino": l["lider_termino"],
        "termino": _fmt_datahora(termino),
        "duracao_min": duracao_min,
        "status": "Finalizado" if termino else ("Em andamento" if inicio else ""),
    }


# ----------------------------------------------------------------------------- operações
def listar():
    with TRAVA:
        wb, ws = _abrir()
        linhas = _linhas(ws)
        linhas.sort(key=lambda l: l["inicio"] or datetime.min, reverse=True)
        return [_saida(l) for l in linhas]


def ordens_sugeridas():
    """Nomes de ordens já usadas antes, pra sugestão no campo (sem repetir)."""
    with TRAVA:
        wb, ws = _abrir()
        linhas = _linhas(ws)
    vistos, saida = set(), []
    for l in linhas:
        chave = _norm(l["ordem"])
        if chave in vistos:
            continue
        vistos.add(chave)
        saida.append(l["ordem"])
    return saida


def iniciar(ordem, lider):
    ordem = _txt(ordem)
    if not ordem:
        raise ErroPlanilha("Digite o nome da Ordem de Produção.")
    with TRAVA:
        wb, ws = _abrir()
        linhas = _linhas(ws)
        em_andamento = [l for l in linhas if _norm(l["ordem"]) == _norm(ordem) and not l["termino"]]
        if em_andamento:
            raise ErroPlanilha(f'A ordem "{ordem}" já está em andamento (iniciada às {_fmt_datahora(em_andamento[0]["inicio"])}).')
        r = _primeira_linha_vazia(ws)
        rid = uuid.uuid4().hex[:10]
        agora = datetime.now()
        ws.cell(row=r, column=COLS["id"], value=rid)
        ws.cell(row=r, column=COLS["ordem"], value=ordem)
        ws.cell(row=r, column=COLS["lider_inicio"], value=_txt(lider))
        c = ws.cell(row=r, column=COLS["inicio"], value=agora)
        c.number_format = FMT_DATAHORA
        _estilo_linha(ws, r)
        _salvar(wb)
        return _saida({"id": rid, "ordem": ordem, "lider_inicio": _txt(lider), "inicio": agora,
                       "lider_termino": "", "termino": None})


def finalizar(rid, lider):
    with TRAVA:
        wb, ws = _abrir()
        linhas = _linhas(ws)
        alvo = next((l for l in linhas if l["id"] == rid), None)
        if not alvo:
            return None
        if alvo["termino"]:
            raise ErroPlanilha("Essa ordem já foi finalizada. Depois de finalizado, não dá para alterar.")
        r = alvo["row"]
        agora = datetime.now()
        ws.cell(row=r, column=COLS["lider_termino"], value=_txt(lider))
        c = ws.cell(row=r, column=COLS["termino"], value=agora)
        c.number_format = FMT_DATAHORA
        _salvar(wb)
        alvo["lider_termino"], alvo["termino"] = _txt(lider), agora
        return _saida(alvo)


# ----------------------------------------------------------------------------- servidor HTTP
class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _json(self, codigo, obj):
        corpo = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(corpo)

    def _corpo(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n).decode("utf-8")) if n else {}

    def _tratar(self, fn):
        try:
            fn()
        except ErroPlanilha as e:
            self._json(423, {"erro": str(e)})
        except Exception as e:
            self._json(500, {"erro": f"Erro inesperado: {e}"})

    def do_GET(self):
        caminho = self.path.split("?")[0]
        if caminho == "/api/versao":
            return self._json(200, {"versao": VERSAO})
        if caminho == "/api/apontamentos":
            return self._tratar(lambda: self._json(200, listar()))
        if caminho == "/api/ordens-sugeridas":
            return self._tratar(lambda: self._json(200, ordens_sugeridas()))
        if caminho in ("/", "/index.html"):
            try:
                with open(HTML, "rb") as f:
                    dados = f.read()
            except FileNotFoundError:
                return self._json(404, {"erro": "apontamento.html não encontrado na pasta."})
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(dados)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(dados)
            return
        self._json(404, {"erro": "não encontrado"})

    def do_POST(self):
        def acao():
            dados = self._corpo()
            if self.path == "/api/apontamentos/iniciar":
                item = iniciar(dados.get("ordem"), dados.get("lider"))
                return self._json(200, {"ok": True, "item": item})
            if self.path.startswith("/api/apontamentos/") and self.path.endswith("/finalizar"):
                rid = self.path.split("/")[3]
                item = finalizar(rid, dados.get("lider"))
                return self._json(200 if item else 404, {"ok": bool(item), "item": item,
                                                           "erro": "" if item else "Ordem não encontrada. Atualize a página."})
            self._json(404, {"erro": "não encontrado"})
        self._tratar(acao)


def ip_local():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


if __name__ == "__main__":
    try:
        srv = ThreadingHTTPServer(("0.0.0.0", PORTA), Handler)
    except OSError:
        print("=" * 60)
        print(f" A porta {PORTA} já está em uso: provavelmente há um servidor ANTIGO ainda aberto.")
        print(" Feche a outra janela do servidor (ou rode os comandos abaixo) e abra de novo:")
        print(f"   netstat -ano | findstr :{PORTA}")
        print("   taskkill /PID 1234 /F      (troque 1234 pelo número da última coluna)")
        print("=" * 60)
        sys.exit(1)
    print("=" * 60)
    print(" Apontamento de Produção - servidor ligado")
    print(f" Neste computador:  http://localhost:{PORTA}")
    print(f" Para a líder/equipe (mesma rede):  http://{ip_local()}:{PORTA}")
    print(f" Planilha: {XLSX}")
    print(" Deixe esta janela aberta. Para encerrar: Ctrl+C")
    print("=" * 60)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
