#!/usr/bin/env python3
"""Smoke driver for the sap-router-skill CLI skill.

Exercises every CLI surface end-to-end against a throwaway workspace and
asserts exit codes + key output substrings. No live SAP system is needed:
routing is a static lookup table, memory_manager is local file I/O, and
xls_to_bapi parses CSV/XLSX. Pure logic — runs fully offline.

Usage:
    python .claude/skills/run-sap-router-skill/driver.py
    # exits 0 = all checks passed, 1 = a check failed

Paths are resolved relative to the unit root (the sap-router-skill
directory), located two parents up from this file's .claude/skills/<name>/.
"""
import os
import sys
import json
import shutil
import tempfile
import subprocess

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
# .../sap-router-skill/.claude/skills/run-sap-router-skill/driver.py
UNIT_ROOT = os.path.abspath(os.path.join(SKILL_DIR, "..", "..", ".."))
SCRIPTS = os.path.join(UNIT_ROOT, "scripts")
PY = sys.executable

passed = 0
failed = 0


def run(args):
    return subprocess.run(
        [PY] + args, capture_output=True, text=True, cwd=UNIT_ROOT
    )


def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS  {name}")
    else:
        failed += 1
        print(f"  FAIL  {name}  {detail}")


def main():
    work = tempfile.mkdtemp(prefix="zrouter_smoke_")
    mem = os.path.join(work, "MEMORY.md")
    pipe_mem = os.path.join(work, "pipe_mem.md")
    # Hermetic ZROUTER opt-in state: keep the persisted decision inside the temp
    # workspace so the smoke run never touches the real zrouter_optin.json.
    os.environ["SAP_ROUTER_OPTIN_FILE"] = os.path.join(work, "optin.json")
    router = os.path.join(SCRIPTS, "sap_router.py")
    memmgr = os.path.join(SCRIPTS, "memory_manager.py")
    xls = os.path.join(SCRIPTS, "xls_to_bapi.py")
    try:
        # --- routing engine ---
        # Functional WRITE token WITHOUT context -> NO BAPI auto-fired
        # (Req: BAPIs fire only when a real functional action requires them).
        r = run([router, "route", "--action", "MM_CREATE_MATERIAL"])
        check("route write w/o context -> needs-functional-context",
              r.returncode == 0 and "needs-functional-context" in r.stdout, r.stdout)

        # Same token WITH explicit functional context -> BAPI dispatch allowed
        r = run([router, "route", "--action", "MM_CREATE_MATERIAL", "--functional"])
        check("route write --functional -> BAPI dispatch",
              r.returncode == 0 and ("bapi-functional" in r.stdout or "BAPI_MATERIAL_SAVEDATA" in r.stdout), r.stdout)

        r = run([router, "route", "--action", "read_source"])
        check("route dev op -> ARC-1 ADT", "ARC-1 (ADT)" in r.stdout, r.stdout)

        r = run([router, "route", "--action", "sf_read_employee"])
        check("route SF -> sf-mcp", "sf-mcp" in r.stdout, r.stdout)

        r = run([router, "route", "--action", "code_search"])
        check("route code_search -> ARC-1 ADT", "ARC-1 (ADT)" in r.stdout, r.stdout)

        r = run([router, "route", "--action", "SE16_DATA"])
        check("route read/admin -> SAP GUI (SE16)", r.returncode == 0 and "SE16" in r.stdout, r.stdout)

        r = run([router, "route"])  # missing --action
        check("route missing --action -> exit 1", r.returncode == 1, f"rc={r.returncode}")

        # --- ZROUTER opt-in (optional accelerator, never the engine) ---
        r = run([router, "zrouter", "decline"])
        check("zrouter decline persists", r.returncode == 0 and "declined" in r.stdout, r.stdout)

        r = run([router, "zrouter", "status"])
        check("zrouter status declined+disabled",
              '"optin": "declined"' in r.stdout and '"enabled": false' in r.stdout, r.stdout)

        # functional write + --use-zrouter while DECLINED -> must NOT use ZROUTER
        r = run([router, "route", "--action", "MM_CREATE_MATERIAL", "--functional", "--use-zrouter"])
        check("declined -> ZROUTER not used", r.returncode == 0 and "zrouter-rfc" not in r.stdout, r.stdout)

        r = run([router, "zrouter", "accept"])
        check("zrouter accept persists", r.returncode == 0 and "accepted" in r.stdout, r.stdout)

        r = run([router, "zrouter", "status"])
        check("zrouter status accepted+enabled",
              '"optin": "accepted"' in r.stdout and '"enabled": true' in r.stdout, r.stdout)

        r = run([router, "zrouter", "reset"])
        check("zrouter reset -> unasked", r.returncode == 0 and "unasked" in r.stdout, r.stdout)

        # --- parallel subagent dispatch ---
        r = run([router, "dispatch-plan", "--spec-text",
                 "Create class ZCL_FOO and table ZBAR for material inspection lot"])
        check("dispatch-plan emits concurrent waves",
              r.returncode == 0 and '"waves"' in r.stdout and '"concurrent": true' in r.stdout, r.stdout)

        r = run([router, "dispatch-plan", "--spec-text", "x", "--serial"])
        check("dispatch-plan --serial -> no concurrency",
              r.returncode == 0 and '"concurrent": true' not in r.stdout, r.stdout)

        r = run([router, "crew-dispatch", "--task", "find the leak then review the diff"])
        check("crew-dispatch -> parallel investigator+reviewer",
              r.returncode == 0 and "investigator" in r.stdout and "reviewer" in r.stdout
              and '"parallel": true' in r.stdout, r.stdout)

        r = run([router, "pipeline", "--spec-text", "Create class ZCL_X for material",
                 "--memory-file", pipe_mem])
        check("pipeline emits PARALLEL waves",
              r.returncode == 0 and "Wave" in r.stdout and "PARALLEL" in r.stdout, r.stdout)

        # --- memory manager lifecycle ---
        r = run([memmgr, "init", "--input", mem, "--sys", "S4H",
                 "--client", "100", "--env", "DEV", "--usr", "DEVELOPER"])
        check("memory init", r.returncode == 0 and os.path.exists(mem), r.stderr)

        r = run([memmgr, "add", "--input", mem, "--module", "MM",
                 "--action-name", "CreateMaterial", "--status", "OK",
                 "--fields", '{"obj":"MAT123","tr":"S4HK900001"}'])
        check("memory add block", r.returncode == 0, r.stderr)

        r = run([memmgr, "verify", "--input", mem])
        check("memory verify valid -> exit 0", r.returncode == 0 and "VALID" in r.stdout, r.stdout)

        r = run([router, "status", "--memory-file", mem])
        check("status reflects active module", "'mod': 'MM'" in r.stdout, r.stdout)

        # log-action via router wrapper
        r = run([router, "log-action", "--module", "SD", "--action", "CreateOrder",
                 "--status", "OK", "--params", '{"obj":"ORD9"}'])
        check("router log-action", r.returncode == 0, r.stderr)

        # compaction: add 25 blocks, expect <= 20 + ARCHIVE
        for i in range(25):
            run([memmgr, "add", "--input", mem, "--module", "MM",
                 "--action-name", f"Act{i}", "--status", "OK"])
        with open(mem, encoding="utf-8") as f:
            body = f.read()
        check("compaction creates ARCHIVE", "## ARCHIVE" in body, "no archive section")
        check("MEMORY.md within 100 lines", body.count("\n") <= 100, f"lines={body.count(chr(10))}")

        # --- xls_to_bapi ---
        tmpl = os.path.join(work, "tmpl.csv")
        r = run([xls, "template", "--output", tmpl, "--module", "MM", "--action", "CREATE_MATERIAL"])
        check("xls template gen", r.returncode == 0 and os.path.exists(tmpl), r.stderr)

        data = os.path.join(work, "data.csv")
        with open(data, "w", encoding="utf-8", newline="") as f:
            f.write("material,material_type,industry,description,base_uom,plant,stor_loc\n")
            f.write("MAT001,FERT,1,Test Widget,PC,1000,0001\n")
        r = run([xls, "convert", "--input", data, "--module", "MM", "--action", "CREATE_MATERIAL"])
        ok = r.returncode == 0
        try:
            payload = json.loads(r.stdout.split("[", 1)[1].rsplit("]", 1)[0].join(["[", "]"]))
        except Exception:
            payload = None
        check("xls convert ok", ok and payload and payload[0]["material"] == "MAT001", r.stdout)

        bad = os.path.join(work, "bad.csv")
        with open(bad, "w", encoding="utf-8", newline="") as f:
            f.write("material,material_type\nMAT002,\n")
        r = run([xls, "validate", "--input", bad, "--module", "MM", "--action", "CREATE_MATERIAL"])
        check("xls validate missing req -> exit 1", r.returncode == 1 and "Missing required" in r.stdout, r.stdout)

        r = run([xls, "template", "--output", os.path.join(work, "x.csv"), "--module", "ZZ", "--action", "FOO"])
        check("xls unsupported action -> exit 1", r.returncode == 1 and "not supported" in r.stderr, r.stderr)

        # --- xls_to_bapi: new module field templates ---
        for mod, act in [("SD","CREATE_ORDER"), ("FI","POST_DOCUMENT"), ("QM","CREATE_INSPECTION"),
                          ("PP","CREATE_ORDER"), ("WM","GOODS_MOVEMENT"), ("CO","CREATE_INTERNAL_ORDER"),
                          ("HCM","READ_EMPLOYEE"), ("BASIS","CREATE_REQUEST")]:
            t = os.path.join(work, f"{mod}_{act}.csv")
            r = run([xls, "template", "--output", t, "--module", mod, "--action", act])
            check(f"xls template {mod}_{act}", r.returncode == 0 and os.path.exists(t), r.stderr)

        # --- xls_to_bapi: convert new modules ---
        sd_csv = os.path.join(work, "sd_order.csv")
        with open(sd_csv, "w", encoding="utf-8", newline="") as f:
            f.write("doc_type,sales_org,dist_channel,division,customer,material,quantity,price\n")
            f.write("TA,1000,01,01,CUST001,MATX,10,150.00\n")
        r = run([xls, "convert", "--input", sd_csv, "--module", "SD", "--action", "CREATE_ORDER"])
        check("xls convert SD CREATE_ORDER", r.returncode == 0 and "CUST001" in r.stdout, r.stderr)

        fi_csv = os.path.join(work, "fi_doc.csv")
        with open(fi_csv, "w", encoding="utf-8", newline="") as f:
            f.write("comp_code,doc_type,doc_date,posting_date,currency,amount,account\n")
            f.write("1000,SA,2026-06-01,2026-06-01,BRL,5000.00,400000\n")
        r = run([xls, "convert", "--input", fi_csv, "--module", "FI", "--action", "POST_DOCUMENT"])
        check("xls convert FI POST_DOCUMENT", r.returncode == 0 and "400000" in r.stdout, r.stderr)

        # --- xls_to_bapi: new code search templates ---
        for mod, act in [("BASIS","CODE_SEARCH"), ("BASIS","CODE_SEARCH_STATS"), ("BASIS","CODE_SEARCH_ADT")]:
            t = os.path.join(work, f"{mod}_{act}.csv")
            r = run([xls, "template", "--output", t, "--module", mod, "--action", act])
            check(f"xls template {mod}_{act}", r.returncode == 0 and os.path.exists(t), r.stderr)

        # --- xls_to_bapi: convert CODE_SEARCH ---
        cs_csv = os.path.join(work, "code_search.csv")
        with open(cs_csv, "w", encoding="utf-8", newline="") as f:
            f.write("query,mode,object_type,package,max_results\n")
            f.write("CALL FUNCTION,STRING,CLAS,ZFOO,50\n")
        r = run([xls, "convert", "--input", cs_csv, "--module", "BASIS", "--action", "CODE_SEARCH"])
        check("xls convert BASIS CODE_SEARCH", r.returncode == 0 and "CALL FUNCTION" in r.stdout, r.stderr)

        # --- xls_to_bapi: convert CO, HCM, BASIS ---
        co_csv = os.path.join(work, "co_order.csv")
        with open(co_csv, "w", encoding="utf-8", newline="") as f:
            f.write("order_type,controlling_area,cost_center,description,currency\n")
            f.write("0100,S4H_CA,CC001,Test CO Order,BRL\n")
        r = run([xls, "convert", "--input", co_csv, "--module", "CO", "--action", "CREATE_INTERNAL_ORDER"])
        check("xls convert CO CREATE_INTERNAL_ORDER", r.returncode == 0 and "S4H_CA" in r.stdout, r.stderr)

        hcm_csv = os.path.join(work, "hcm_emp.csv")
        with open(hcm_csv, "w", encoding="utf-8", newline="") as f:
            f.write("employee_id,infotype,subtype,begin_date,end_date\n")
            f.write("12345,0001,,2026-01-01,2026-12-31\n")
        r = run([xls, "convert", "--input", hcm_csv, "--module", "HCM", "--action", "READ_EMPLOYEE"])
        check("xls convert HCM READ_EMPLOYEE", r.returncode == 0 and "12345" in r.stdout, r.stderr)

        basis_csv = os.path.join(work, "basis_tr.csv")
        with open(basis_csv, "w", encoding="utf-8", newline="") as f:
            f.write("request_type,owner_text,target_system\n")
            f.write("K,Bulk material import from XLS,\n")
        r = run([xls, "convert", "--input", basis_csv, "--module", "BASIS", "--action", "CREATE_REQUEST"])
        check("xls convert BASIS CREATE_REQUEST", r.returncode == 0 and "Bulk material" in r.stdout, r.stderr)

        # --- template_repo ---
        tmpl = os.path.join(SCRIPTS, "template_repo.py")
        r = run([tmpl, "init"])
        check("template_repo init", r.returncode == 0, r.stderr)

        r = run([tmpl, "seed"])
        check("template_repo seed", r.returncode == 0, r.stderr)

        r = run([tmpl, "list"])
        check("template_repo list shows templates", "12 templates" in r.stdout, r.stdout)

        r = run([tmpl, "resolve", "--template", "MM_CREATE_MATERIAL",
                 "--values", '{"HEADER":"h","DESCRIPTION":"d","RETURN_STRUCT":"r","MATERIAL_NUMBER":"m","DESCRIPTION_TABLE":"t"}'])
        check("template_repo resolve MM_CREATE_MATERIAL", r.returncode == 0 and "BAPI_MATERIAL_SAVEDATA" in r.stdout, r.stderr)

        # Clean up seeded repo to avoid polluting workspace
        shutil.rmtree(os.path.join(UNIT_ROOT, "template_repo"), ignore_errors=True)

        # --- cpi_iflow_packager ---
        cpi_pkg = os.path.join(SCRIPTS, "cpi_iflow_packager.py")
        # template
        cpi_zip = os.path.join(work, "test-iflow.zip")
        r = run([cpi_pkg, "template", "--name", "test-iflow", "--output", cpi_zip])
        check("cpi packager template", r.returncode == 0 and os.path.exists(cpi_zip), r.stderr)

        # list
        r = run([cpi_pkg, "list", "--input", cpi_zip])
        check("cpi packager list", r.returncode == 0 and "flow.xml" in r.stdout, r.stderr)

        # validate
        r = run([cpi_pkg, "validate", "--input", cpi_zip])
        check("cpi packager validate", r.returncode == 0 and "VALID" in r.stdout, r.stderr)

        # create custom
        cpi_custom = os.path.join(work, "custom-iflow.zip")
        r = run([cpi_pkg, "create", "--name", "custom-iflow", "--output", cpi_custom])
        check("cpi packager create", r.returncode == 0 and os.path.exists(cpi_custom), r.stderr)

        # validate custom
        r = run([cpi_pkg, "validate", "--input", cpi_custom])
        check("cpi packager validate custom", r.returncode == 0 and "VALID" in r.stdout, r.stderr)

        # extract
        cpi_extract = os.path.join(work, "cpi_extracted")
        r = run([cpi_pkg, "extract", "--input", cpi_zip, "--output", cpi_extract])
        check("cpi packager extract", r.returncode == 0 and os.path.exists(
            os.path.join(cpi_extract, "src", "main", "resources", "flow.xml")), r.stderr)

        # --- abap_serializer ---
        aser = os.path.join(SCRIPTS, "abap_serializer.py")
        # Write a test ABAP class source
        abap_src = os.path.join(work, "zcl_test.abap")
        with open(abap_src, "w", encoding="utf-8") as f:
            f.write("CLASS zcl_test DEFINITION PUBLIC FINAL CREATE PUBLIC.\n")
            f.write("  PUBLIC SECTION.\n")
            f.write("    METHODS hello.\n")
            f.write("ENDCLASS.\n\n")
            f.write("CLASS zcl_test IMPLEMENTATION.\n")
            f.write("  METHOD hello.\n")
            f.write("    WRITE: / 'Hello from ABAP serializer!'.\n")
            f.write("  ENDMETHOD.\n")
            f.write("ENDCLASS.\n")

        # list-formats
        r = run([aser, "list-formats"])
        check("abap_serializer list-formats", r.returncode == 0 and "nugg" in r.stdout, r.stderr)

        # generate nugg
        nugg_dir = os.path.join(work, "nugg_out")
        r = run([aser, "generate", "--source", abap_src, "--name", "ZCL_TEST",
                 "--type", "CLAS", "--format", "nugg", "--output", nugg_dir])
        nugg_file = os.path.join(nugg_dir, "zcl_test.nugg")
        check("abap_serializer generate nugg", r.returncode == 0 and os.path.exists(nugg_file), r.stderr)

        # generate abapgit
        ag_dir = os.path.join(work, "abapgit_out")
        r = run([aser, "generate", "--source", abap_src, "--name", "ZCL_TEST",
                 "--type", "CLAS", "--format", "abapgit", "--output", ag_dir])
        ag_xml = os.path.join(ag_dir, "zcl_test.clas.xml")
        ag_abap = os.path.join(ag_dir, "zcl_test.clas.abap")
        check("abap_serializer generate abapgit", r.returncode == 0
              and os.path.exists(ag_xml) and os.path.exists(ag_abap), r.stderr)

        # generate xml (ZDOWNLOAD)
        xml_dir = os.path.join(work, "xml_out")
        r = run([aser, "generate", "--source", abap_src, "--name", "ZCL_TEST",
                 "--type", "CLAS", "--format", "xml", "--output", xml_dir])
        xml_file = os.path.join(xml_dir, "zcl_test_zdload.xml")
        check("abap_serializer generate xml", r.returncode == 0 and os.path.exists(xml_file), r.stderr)

        # extract from nugg
        ext_dir = os.path.join(work, "extracted")
        r = run([aser, "extract", "--input", nugg_file, "--output", ext_dir])
        check("abap_serializer extract nugg", r.returncode == 0
              and "ZCL_TEST" in r.stdout, r.stderr)

        # split multi-class ABAP
        multi_src = os.path.join(work, "multi_class.abap")
        with open(multi_src, "w", encoding="utf-8") as f:
            f.write("CLASS zcl_one DEFINITION PUBLIC FINAL CREATE PUBLIC.\n")
            f.write("  PUBLIC SECTION.\n")
            f.write("    METHODS run.\n")
            f.write("ENDCLASS.\n\n")
            f.write("CLASS zcl_one IMPLEMENTATION.\n")
            f.write("  METHOD run.\n")
            f.write("    WRITE: / 'one'.\n")
            f.write("  ENDMETHOD.\n")
            f.write("ENDCLASS.\n\n")
            f.write("INTERFACE zif_two.\n")
            f.write("  METHODS do.\n")
            f.write("ENDINTERFACE.\n")
        split_dir = os.path.join(work, "split_out")
        r = run([aser, "split", "--source", multi_src, "--output", split_dir])
        check("abap_serializer split multi-object", r.returncode == 0
              and "zcl_one" in r.stdout and "zif_two" in r.stdout, r.stderr)

        # package (all 3 formats at once)
        pkg_dir = os.path.join(work, "packaged")
        r = run([aser, "package", "--source", abap_src, "--name", "ZCL_TEST",
                 "--type", "CLAS", "--output", pkg_dir])
        pkg_nugg = os.path.join(pkg_dir, "nugg", "zcl_test.nugg")
        check("abap_serializer package all formats", r.returncode == 0
              and os.path.exists(pkg_nugg), r.stderr)

    finally:
        shutil.rmtree(work, ignore_errors=True)

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
