#!/usr/bin/env python
"""O fonte do gateway existe em dois lugares. Este script prova que são o mesmo.

`ZCL_ZROUTER_GW.clas.abap` é a cópia legível — a que abaplint e um revisor leem.
`ZROUTER_V5_INSTALL.abap` carrega o mesmo fonte como tabela de strings, porque um
REPORT é o único artefato ABAP que se instala com copiar/colar e sem dependência,
que é o problema que o instalador existe para resolver.

Duas cópias divergem. A que ninguém executa é a que é revisada, e a revisão passa
a atestar um código que não é o instalado — que é pior do que não revisar. Daí
este gate: falha ruidosamente na primeira linha divergente.

Uso:  python deploy/zrouter-v5/check_sync.py
Saída: 0 se idênticos, 1 com o diff se não.
"""
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
INSTALADOR = AQUI / "ZROUTER_V5_INSTALL.abap"
CLASSE = AQUI / "ZCL_ZROUTER_GW.clas.abap"

# O cabeçalho da cópia legível é comentário sobre a própria duplicação; ele não
# existe no instalador e não deve entrar na comparação.
CABECALHO = re.compile(r"\A(?:\*.*\n)+")


def fonte_embutido(texto: str) -> list[str]:
    """As linhas que o instalador emite via `_a `...`.` — na ordem."""
    linhas = []
    for m in re.finditer(r"^\s*_a (?:`(.*)`|``)\.\s*$", texto, re.M):
        linhas.append(m.group(1) if m.group(1) is not None else "")
    return linhas


def main() -> int:
    for caminho in (INSTALADOR, CLASSE):
        if not caminho.is_file():
            print(f"FALHA: {caminho.name} não existe")
            return 1

    embutido = fonte_embutido(INSTALADOR.read_text(encoding="utf-8"))
    if not embutido:
        print("FALHA: nenhuma linha `_a` encontrada no instalador — o padrão mudou?")
        return 1

    legivel = CABECALHO.sub("", CLASSE.read_text(encoding="utf-8")).splitlines()
    # splitlines() de um arquivo terminado em \n não gera linha final vazia,
    # e a lista embutida também não tem — nada a normalizar além disso.

    if embutido == legivel:
        print(f"OK: {len(embutido)} linhas idênticas nos dois arquivos")
        return 0

    print(f"DIVERGEM: instalador tem {len(embutido)} linhas, cópia legível tem {len(legivel)}")
    for i in range(max(len(embutido), len(legivel))):
        a = embutido[i] if i < len(embutido) else "<ausente>"
        b = legivel[i] if i < len(legivel) else "<ausente>"
        if a != b:
            print(f"  primeira diferença na linha {i + 1}:")
            print(f"    instalador: {a!r}")
            print(f"    classe    : {b!r}")
            break
    return 1


if __name__ == "__main__":
    sys.exit(main())
