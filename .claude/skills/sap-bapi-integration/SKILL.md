---
name: sap-bapi-integration
description: SAP BAPI/RFC integration — BAPI discovery, transaction handling, BAPIRET2 patterns, 29 BAPI mappings across 9 modules (MM/SD/FI/QM/PP/WM/CO/HCM/BASIS). Use for BAPI calls, CSV→BAPI conversion, ZROUTER handler creation, or BAPI debugging.
trigger: bapi, BAPI, rfc, RFC, transaction commit, BAPIRET2, BAPI_TRANSACTION, goods movement, sales order bapi, material bapi, purchase order bapi, criar material, criar pedido, posting document, ZROUTER handler
---

# SAP BAPI Integration — 9 Modules, 29 BAPIs

> **Pré-requisitos:** SAP RFC connection, ZROUTER_DISPATCH_FM (ou BAPI direto), Python 3.8+.

## Quando usar

- Criar/modificar materiais, pedidos, docs FI via BAPI
- Mapear campos CSV/XLS para parâmetros BAPI
- Debuggar BAPIRET2 — a mensagem de erro real nunca está no sy-subrc
- Criar handler ZROUTER para novo módulo funcional
- Substituir batch input/BDC por BAPI (ex: MB01 → BAPI_GOODSMVT_CREATE)

## Regra de Ouro BAPI

```
1. BAPI_<OBJETO>_<AÇÃO>  → chamar com parâmetros por VALOR
2. Checar BAPIRET2-TYPE   → NUNCA confiar em sy-subrc
3. E ou A no TYPE?        → BAPI_TRANSACTION_ROLLBACK
4. Senão                  → BAPI_TRANSACTION_COMMIT EXPORTING wait = 'X'
```

## Passo a passo

### 1. Descobrir BAPI

```bash
# Buscar na documentação SAP local
python scripts/sap_router.py route --action CREATE_MATERIAL --module MM
# → "ZROUTER RFC"

# Listar BAPIs de um módulo
grep -A1 "CREATE_MATERIAL\|CREATE_PO\|CREATE_ORDER\|POST_DOCUMENT" \
  scripts/xls_to_bapi.py
```

### 2. Converter CSV → payload BAPI

```bash
# Gerar template
python scripts/xls_to_bapi.py template \
  --output tmpl.csv --module MM --action CREATE_MATERIAL

# Converter dados
python scripts/xls_to_bapi.py convert \
  --input data.csv --module MM --action CREATE_MATERIAL
# Esperado: JSON com payload BAPI_MATERIAL_SAVEDATA
```

### 3. Chamar BAPI (ABAP)

```abap
DATA: ls_header  TYPE bapimathead,
      ls_ret     TYPE bapiret2,
      lt_ret     TYPE bapiret2_t,
      lv_matnr   TYPE matnr,
      lt_desc    TYPE TABLE OF bapi_makt.

" Preencher header
ls_header-material      = 'M-001'.
ls_header-matl_type     = 'FERT'.
ls_header-indust_sector = 'M'.

CALL FUNCTION 'BAPI_MATERIAL_SAVEDATA'
  EXPORTING
    headdata = ls_header
  IMPORTING
    return   = ls_ret
    material = lv_matnr
  TABLES
    materialdescription = lt_desc.

" ⚠️ Checar TYPE, NÃO sy-subrc
IF ls_ret-type CA 'EA'.              " Error ou Abort
  CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
ELSE.
  CALL FUNCTION 'BAPI_TRANSACTION_COMMIT'
    EXPORTING wait = 'X'.
ENDIF.
```

### 4. Verificar

```bash
# Validar via sap_router
python scripts/sap_router.py log-action \
  --action CREATE_MATERIAL --module MM --status OK --details "MATNR: 000000000000001234"

# Checar memory
python scripts/memory_manager.py verify \
  --input MEMORY.md
```

## BAPIRET2 — A Chave do Debug

| Campo | Significado | Exemplo |
|---|---|---|
| TYPE | S=OK, W=Warning, **E=Error, A=Abort**, I=Info | `E` |
| ID | Classe de mensagem | `M3` |
| NUMBER | Nº da mensagem | `001` |
| MESSAGE | Texto traduzido | "Material M-001 created" |
| MESSAGE_V1..V4 | Variáveis da mensagem | M-001, FERT, ... |
| PARAMETER | Campo que causou erro | `HEADDATA-MATERIAL` |
| ROW | Linha da tabela (se aplicável) | `3` |

**Código real de produção (extraído do ABAP LLM via RAG):**
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

## 9 Módulos — BAPIs e Tabelas

### MM — Materials Management
| BAPI | Propósito | Tabelas-Chave |
|---|---|---|
| `BAPI_MATERIAL_SAVEDATA` | Criar/alterar material | MARA, MARC, MAKT |
| `BAPI_MATERIAL_GETALL` | Listar materiais | MARA |
| `BAPI_PO_CREATE1` | Criar pedido de compra | EKKO, EKPO |
| `BAPI_PO_CHANGE` | Alterar pedido | EKKO, EKPO |
| `BAPI_GOODSMVT_CREATE` | Movimento de mercadoria | MSEG, MKPF |

```bash
# Template CSV
python scripts/xls_to_bapi.py template \
  --module MM --action CREATE_PO
```

### SD — Sales & Distribution
| BAPI | Propósito | Tabelas-Chave |
|---|---|---|
| `BAPI_SALESORDER_CREATEFROMDAT2` | Criar ordem de venda | VBAK, VBAP |
| `BAPI_SALESORDER_CHANGE` | Alterar ordem | VBAK, VBAP |
| `BAPI_BILLINGDOC_CREATEMULTIPLE` | Criar fatura (VF01) | VBRK, VBRP |
| `BAPI_OUTB_DELIVERY_CREATE_SLS` | Criar entrega (VL01N) | LIKP, LIPS |

**Fluxo SD padrão:** TA (order VA01) → LF (delivery VL01N) → F2 (billing VF01)

```bash
# Criar ordem de venda via CSV
python scripts/xls_to_bapi.py template \
  --module SD --action CREATE_ORDER
```

### FI — Financial Accounting
| BAPI | Propósito |
|---|---|
| `BAPI_ACC_DOCUMENT_POST` | Postar documento contábil |
| `BAPI_ACC_DOCUMENT_REV_POST` | Estornar documento |
| `BAPI_GL_GETACCOUNTSALDO` | Consultar saldo contábil |

```bash
python scripts/xls_to_bapi.py template \
  --module FI --action POST_DOCUMENT
```

### QM — Quality Management
| BAPI | Propósito |
|---|---|
| `CO_QM_INSPECTION_LOT_CREATE` | Criar lote de inspeção |
| `BAPI_INSPOPER_RECORDRESULTS` | Registrar resultados |

### PP — Production Planning
| BAPI | Propósito |
|---|---|
| `BAPI_PRODORD_CREATE` | Criar ordem de produção |
| `BAPI_PRODORDCONF_CREATE_TT` | Confirmar ordem |
| `CS_BOM_EXPL_MAT_V2` | Explodir BOM |
| `BAPI_ROUTING_GETDETAIL` | Ler roteiro |

### WM — Warehouse Management
| BAPI | Propósito |
|---|---|
| `BAPI_GOODSMVT_CREATE` | Movimento de mercadoria |
| `L_TO_CREATE_SINGLE` | Criar ordem de transferência |

### CO — Controlling
| BAPI | Propósito |
|---|---|
| `BAPI_INTERNALORDER_CREATE` | Criar ordem interna |
| `BAPI_CO_ALLOCACTUALS` | Alocar custos reais |

### HCM — Human Capital Management
| BAPI | Propósito |
|---|---|
| `BAPI_EMPLOYEE_GETDATA` | Ler dados do empregado |
| `PA_INFOTYPE_INSERT` | Criar infotipo (⚠️ requer ENQUEUE antes) |

### BASIS — System Administration
| BAPI/FM | Propósito |
|---|---|
| `TR_INSERT_REQUEST_WITH_TASKS` | Criar request de transporte |
| `TR_RELEASE_REQUEST` | Liberar request |
| `TRINT_INSPECT_OBJECTS` | Analisar objetos |

## ⚠️ Pitfalls

- **sy-subrc ≠ BAPIRET2-TYPE** → BAPI sempre retorna 0, o erro está no BAPIRET2. **NUNCA** `IF sy-subrc <> 0` para validar BAPI
- **COMMIT vs COMMIT WORK** → Sempre use `BAPI_TRANSACTION_COMMIT`, nunca `COMMIT WORK` direto. O BAPI commit garante update síncrono
- **Parâmetros por valor** → BAPIs não suportam pass-by-reference. Todos os parâmetros devem ser passados por valor
- **Lock antes de update** → Para HCM/PA_INFOTYPE_INSERT sempre faça ENQUEUE antes. Para MM use BAPI_MATERIAL_SAVEDATA que já locka
- **QM usa prefixo CO_** → BAPIs de qualidade usam `CO_QM_*`, não `BAPI_QM_*`
- **L_TO_CREATE_SINGLE é RFC, não BAPI** → Não tem BAPIRET2, checar retorno específico
- **Implicit commits** → Dialog step, RFC calls, CALL TRANSACTION, SUBMIT, WAIT — todos disparam commit implícito. Cuidado com SAP LUWs longas
- **Rollback implícito** → Runtime error (dump), mensagem tipo A ou X, PBO com erro — reseta tudo

## Template completo — Handler ZROUTER

```bash
# Gerar ABAP com placeholders resolvidos
python scripts/template_repo.py resolve \
  --template MM_CREATE_MATERIAL \
  --values '{"HEADER":"ls_header","DESCRIPTION":"ls_desc","RETURN_STRUCT":"ls_ret","MATERIAL_NUMBER":"lv_matnr","DESCRIPTION_TABLE":"lt_desc"}'
```
