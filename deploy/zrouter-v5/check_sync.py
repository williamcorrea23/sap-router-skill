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


# Dependência de DDIC resolvida em COMPILAÇÃO. Se qualquer uma destas aparecer
# no código do instalador (fora das linhas `_a`, que são a classe embutida, e
# fora de literais string), o programa deixa de ativar num sistema onde as
# tabelas ainda não existem — que é o único sistema onde ele serve para alguma
# coisa. Foi assim que a primeira versão quebrou, e um comentário pedindo
# cuidado não impede a próxima; este gate impede.
ESTATICO = re.compile(
    r"\b(?:TYPE|LIKE)\s+(zrouter_\w+)\b"
    r"|\b(?:MODIFY|INSERT|UPDATE|DELETE\s+FROM|SELECT\s+.*\bFROM)\s+(zrouter_\w+)\b",
    re.I,
)


def referencias_estaticas(texto: str) -> list[tuple[int, str]]:
    """Linhas do instalador que amarram uma tabela ZROUTER em tempo de compilação."""
    achados = []
    for numero, linha in enumerate(texto.splitlines(), start=1):
        sem_espaco = linha.lstrip()
        # A classe embutida vive em linhas `_a` e é compilada no SAP, não aqui.
        if sem_espaco.startswith("_a "):
            continue
        # Comentário ABAP: linha inteira (*) ou a partir da aspa dupla.
        if sem_espaco.startswith("*"):
            continue
        codigo = linha.split('"', 1)[0]
        # Nome de tabela dentro de literal é dado, não dependência.
        codigo = re.sub(r"'[^']*'", "''", codigo)
        m = ESTATICO.search(codigo)
        if m:
            achados.append((numero, linha.strip()))
    return achados


def main() -> int:
    for caminho in (INSTALADOR, CLASSE):
        if not caminho.is_file():
            print(f"FALHA: {caminho.name} não existe")
            return 1

    texto_inst = INSTALADOR.read_text(encoding="utf-8")

    estaticas = referencias_estaticas(texto_inst)
    if estaticas:
        print("FALHA: o instalador referencia tabela ZROUTER em tempo de compilação.")
        print("  Com isso ele não ativa num sistema onde a tabela ainda não existe,")
        print("  que é exatamente onde ele precisa rodar. Use acesso dinâmico:")
        print("  CREATE DATA ... TYPE (lv_tab) / MODIFY (lv_tab) FROM @<ls_row>.")
        for numero, linha in estaticas:
            print(f"    linha {numero}: {linha}")
        return 1

    embutido = fonte_embutido(texto_inst)
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
