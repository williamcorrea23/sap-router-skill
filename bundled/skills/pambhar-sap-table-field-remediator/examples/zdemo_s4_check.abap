*&---------------------------------------------------------------------*
*& Demo program for the SAP Table & Field Remediator skill.
*& Hand-written sample (NOT the eval corpus) so you can try the skill
*& with zero code of your own. It deliberately mixes must-fix accesses
*& with a benign one, to show detection + tiering + suppression.
*&---------------------------------------------------------------------*
REPORT zdemo_s4_check.

DATA: lt_items TYPE TABLE OF bseg,
      ls_vbuk  TYPE vbuk,
      lv_matnr TYPE matnr,
      lt_konv  TYPE TABLE OF konv.

" T3 / semantic — BSEG line items moved into the Universal Journal (ACDOCA).
SELECT * FROM bseg INTO TABLE lt_items
  WHERE bukrs = '1000' AND gjahr = '2024'.

" T2 / structural — header status table VBUK folded into VBAK/VBAP in S/4.
SELECT SINGLE * FROM vbuk INTO ls_vbuk WHERE vbeln = '0000012345'.

" T3 / functional — KONV pricing cluster abolished; reads go to PRCD_ELEMENTS.
SELECT * FROM konv INTO TABLE lt_konv WHERE knumv = '0000098765'.

" T1 / syntactic — MATNR extended 18 -> 40; plain assignment is fine, but
" an offset slice that assumes the old 18-char layout would escalate.
lv_matnr = '000000000000123456'.

" Benign — MARA is VALID in S/4; a plain read must NOT be flagged.
SELECT SINGLE matnr FROM mara INTO lv_matnr WHERE matnr = lv_matnr.

WRITE: / 'done'.
