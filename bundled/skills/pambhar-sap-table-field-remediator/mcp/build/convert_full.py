#!/usr/bin/env python3
"""Full conversion of the SAP Simplification List PDF -> DoclingDocument JSON.

Accurate tables, no OCR (born-digital text; OCR would only add noise). One-time.
Writes full.json (export_to_dict) for the chunker to consume.
"""
import time, json
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode

opts = PdfPipelineOptions()
opts.do_ocr = False
opts.do_table_structure = True
opts.table_structure_options.mode = TableFormerMode.ACCURATE

conv = DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)})
t0 = time.time()
res = conv.convert("simplification-list-2023.pdf")
dt = time.time() - t0
d = res.document.export_to_dict()
json.dump(d, open("full.json", "w"))
res.document.save_as_markdown("full.md")
print(f"DONE in {dt/60:.1f} min | texts {len(d.get('texts',[]))} | tables {len(d.get('tables',[]))}")
print("wrote full.json + full.md")
