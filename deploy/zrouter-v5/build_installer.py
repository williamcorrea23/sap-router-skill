#!/usr/bin/env python
"""Injeta o fonte canônico do gateway dentro do instalador.

`ZCL_ZROUTER_GW.clas.abap` é a verdade: é o arquivo que abaplint lê e que um
revisor abre. O instalador precisa do mesmo fonte como tabela de strings,
porque um REPORT é o único artefato ABAP que se instala com copiar/colar e sem
dependência nenhuma — que é o problema que ele existe para resolver.

Manter as duas cópias à mão garantiria que divergissem. Então uma é gerada.

Uso:
    python deploy/zrouter-v5/build_installer.py
    python deploy/zrouter-v5/check_sync.py     # prova que ficaram iguais
"""
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CLASSE = AQUI / "ZCL_ZROUTER_GW.clas.abap"
INSTALADOR = AQUI / "ZROUTER_V5_INSTALL.abap"

INICIO = "    _a `CLASS zcl_zrouter_gw DEFINITION PUBLIC FINAL CREATE PUBLIC.`."
FIM_METODO = "  ENDMETHOD.\n\n  METHOD install."

# O cabeçalho da classe é comentário sobre o próprio arquivo e sobre o gerador;
# não faz sentido dentro do instalador, que já explica o mesmo em outro lugar.
CABECALHO = re.compile(r"\A(?:\*.*\n)+")


def emitir(linhas: list[str]) -> str:
    """Cada linha vira `_a `...`.` — string ABAP delimitada por backtick."""
    saida = []
    for i, linha in enumerate(linhas, start=1):
        if "`" in linha:
            raise SystemExit(
                f"FALHA: backtick na linha {i} do fonte da classe.\n"
                f"  {linha!r}\n"
                "  O gerador delimita cada linha com backtick; um backtick no "
                "fonte encerraria a string ABAP no meio. Use aspas simples."
            )
        saida.append("    _a ``." if linha == "" else f"    _a `{linha}`.")
    return "\n".join(saida)


def main() -> int:
    if not CLASSE.is_file() or not INSTALADOR.is_file():
        print("FALHA: arquivo de origem ou destino ausente")
        return 1

    fonte = CABECALHO.sub("", CLASSE.read_text(encoding="utf-8"))
    linhas = fonte.splitlines()
    if not linhas or "CLASS zcl_zrouter_gw DEFINITION" not in linhas[0]:
        print("FALHA: a classe não começa com a declaração esperada após o cabeçalho")
        return 1

    inst = INSTALADOR.read_text(encoding="utf-8")
    i = inst.find(INICIO)
    if i < 0:
        print("FALHA: marcador de início não encontrado no instalador")
        return 1
    j = inst.find(FIM_METODO, i)
    if j < 0:
        print("FALHA: fim do método source não encontrado")
        return 1

    novo = inst[:i] + emitir(linhas) + "\n" + inst[j:]
    INSTALADOR.write_text(novo, encoding="utf-8")
    print(f"OK: {len(linhas)} linhas injetadas em {INSTALADOR.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
