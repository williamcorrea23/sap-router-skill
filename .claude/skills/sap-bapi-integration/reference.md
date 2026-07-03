# BAPI Reference — 9 Modules, 29 BAPIs

> Full reference tables for [SKILL.md](SKILL.md)

## BAPIRET2 Field Reference

| Campo | Significado | Exemplo |
|---|---|---|
| TYPE | S=OK, W=Warning, **E=Error, A=Abort**, I=Info | `E` |
| ID | Classe de mensagem | `M3` |
| NUMBER | Nº da mensagem | `001` |
| MESSAGE | Texto traduzido | "Material M-001 created" |
| MESSAGE_V1..V4 | Variáveis da mensagem | M-001, FERT, ... |
| PARAMETER | Campo que causou erro | `HEADDATA-MATERIAL` |
| ROW | Linha da tabela (se aplicável) | `3` |

## MM — Materials Management

| BAPI | Propósito | Tabelas-Chave |
|---|---|---|
| `BAPI_MATERIAL_SAVEDATA` | Criar/alterar material | MARA, MARC, MAKT |
| `BAPI_MATERIAL_GETALL` | Listar materiais | MARA |
| `BAPI_PO_CREATE1` | Criar pedido de compra | EKKO, EKPO |
| `BAPI_PO_CHANGE` | Alterar pedido | EKKO, EKPO |
| `BAPI_GOODSMVT_CREATE` | Movimento de mercadoria | MSEG, MKPF |

```bash
python scripts/xls_to_bapi.py template --module MM --action CREATE_PO
```

## SD — Sales & Distribution

| BAPI | Propósito | Tabelas-Chave |
|---|---|---|
| `BAPI_SALESORDER_CREATEFROMDAT2` | Criar ordem de venda | VBAK, VBAP |
| `BAPI_SALESORDER_CHANGE` | Alterar ordem | VBAK, VBAP |
| `BAPI_BILLINGDOC_CREATEMULTIPLE` | Criar fatura (VF01) | VBRK, VBRP |
| `BAPI_OUTB_DELIVERY_CREATE_SLS` | Criar entrega (VL01N) | LIKP, LIPS |

Fluxo SD padrão: TA (order VA01) → LF (delivery VL01N) → F2 (billing VF01)

## FI — Financial Accounting

| BAPI | Propósito |
|---|---|
| `BAPI_ACC_DOCUMENT_POST` | Postar documento contábil |
| `BAPI_ACC_DOCUMENT_REV_POST` | Estornar documento |
| `BAPI_GL_GETACCOUNTSALDO` | Consultar saldo contábil |

## QM — Quality Management

| BAPI | Propósito |
|---|---|
| `CO_QM_INSPECTION_LOT_CREATE` | Criar lote de inspeção |
| `BAPI_INSPOPER_RECORDRESULTS` | Registrar resultados |

## PP — Production Planning

| BAPI | Propósito |
|---|---|
| `BAPI_PRODORD_CREATE` | Criar ordem de produção |
| `BAPI_PRODORDCONF_CREATE_TT` | Confirmar ordem |
| `CS_BOM_EXPL_MAT_V2` | Explodir BOM |
| `BAPI_ROUTING_GETDETAIL` | Ler roteiro |

## WM — Warehouse Management

| BAPI | Propósito |
|---|---|
| `BAPI_GOODSMVT_CREATE` | Movimento de mercadoria |
| `L_TO_CREATE_SINGLE` | Criar ordem de transferência |

## CO — Controlling

| BAPI | Propósito |
|---|---|
| `BAPI_INTERNALORDER_CREATE` | Criar ordem interna |
| `BAPI_CO_ALLOCACTUALS` | Alocar custos reais |

## HCM — Human Capital Management

| BAPI | Propósito |
|---|---|
| `BAPI_EMPLOYEE_GETDATA` | Ler dados do empregado |
| `PA_INFOTYPE_INSERT` | Criar infotipo (requer ENQUEUE antes) |

## BASIS — System Administration

| BAPI/FM | Propósito |
|---|---|
| `TR_INSERT_REQUEST_WITH_TASKS` | Criar request de transporte |
| `TR_RELEASE_REQUEST` | Liberar request |
| `TRINT_INSPECT_OBJECTS` | Analisar objetos |

## Template — Handler ZROUTER

```bash
# Gerar ABAP com placeholders resolvidos
python scripts/template_repo.py resolve \
  --template MM_CREATE_MATERIAL \
  --values '{"HEADER":"ls_header","DESCRIPTION":"ls_desc","RETURN_STRUCT":"ls_ret","MATERIAL_NUMBER":"lv_matnr","DESCRIPTION_TABLE":"lt_desc"}'
```

## BAPIRET2 Production Code (RAG-extracted)

```abap
LOOP AT lt_bapiret ASSIGNING FIELD-SYMBOL(<fs_ret>).
  APPEND INITIAL LINE TO rt_bapiret ASSIGNING FIELD-SYMBOL(<fs_out>).
  <fs_out>-msgty = <fs_ret>-type.
  <fs_out>-msgid = <fs_ret>-id.
  <fs_out>-msgno = <fs_ret>-number.
  <fs_out>-msgv1 = <fs_ret>-message_v1.
  <fs_out>-msgv2 = <fs_ret>-message_v2.
  <fs_out>-msgv3 = <fs_ret>-message_v3.
  <fs_out>-msgv4 = <fs_ret>-message_v4.
ENDLOOP.
```
