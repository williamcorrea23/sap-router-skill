"""Deploy all pending ABAP/DDIC objects to SAP via ADT REST API."""
import subprocess, os, sys
from pathlib import Path

SAP_URL = os.environ.get("ARC_SAP_URL") or os.environ.get("SAP_URL")
SAP_USER = os.environ.get("ARC_SAP_USER") or os.environ.get("SAP_USER")
SAP_PASSWORD = os.environ.get("ARC_SAP_PASSWORD") or os.environ.get("SAP_PASSWORD")
if not SAP_URL or not SAP_USER or not SAP_PASSWORD:
    raise SystemExit("Missing ARC_SAP_URL/ARC_SAP_USER/ARC_SAP_PASSWORD for deploy_all.")

CURL_BASE = ['curl', '-sS', '-u', f'{SAP_USER}:{SAP_PASSWORD}']
if (os.environ.get("SAP_ALLOW_UNAUTHORIZED", "").lower() == "true"
        and os.environ.get("SAP_ENV", "").upper() not in {"PROD", "PRD", "PRODUCTION"}):
    CURL_BASE.insert(1, "-k")
DEPLOY_DIR = Path(__file__).resolve().parent.parent / 'deploy' / 'split2'

def curl_get(path):
    """GET with -i to parse headers. Returns (status, cookie, csrf, etag)."""
    cmd = CURL_BASE + ['-i', '-H', 'x-csrf-token: fetch', SAP_URL + path]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    output = r.stdout
    line_sep = '\r\n' if '\r\n\r\n' in output else '\n'
    parts = output.split(line_sep + line_sep, 1)
    header_section = parts[0]

    status = 200
    first_line = header_section.split(line_sep)[0]
    if 'HTTP' in first_line:
        try: status = int(first_line.split()[1])
        except: pass

    csrf = ''; cookie = ''; etag = ''
    for line in header_section.split(line_sep):
        l = line.lower()
        if l.startswith('x-csrf-token:'):
            csrf = line.split(':', 1)[1].strip()
        if l.startswith('etag:'):
            etag = line.split(':', 1)[1].strip()
            # NW 7.40 bug: ETag might have content-type suffix leaked
            # e.g. "20260705073051000text/plain2" -> strip "text/plain" and digits
            import re
            etag = re.sub(r'text/plain\d*', '', etag).strip()
        if l.startswith('set-cookie:') and 'sap_sessionid' in l.lower():
            cookie = line.split(';')[0].split(':', 1)[1].strip() if ':' in line.split(';')[0] else line.split(';')[0].strip()

    return status, cookie, csrf, etag

def curl_put(path, data, content_type, cookie, csrf, etag):
    """PUT source. Returns (status_code, body)."""
    cmd = list(CURL_BASE)
    cmd += ['-X', 'PUT']
    if csrf: cmd += ['-H', 'x-csrf-token: ' + csrf]
    if content_type: cmd += ['-H', 'Content-Type: ' + content_type]
    if etag: cmd += ['-H', 'If-Match: ' + etag]
    if cookie: cmd += ['-b', cookie]
    cmd += ['--data-binary', '@' + data] if isinstance(data, str) and os.path.exists(data) else ['--data-binary', data]
    cmd += ['-w', '\nSTATUS:%{http_code}']
    cmd.append(SAP_URL + path)

    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    out = r.stdout
    if 'STATUS:' in out:
        parts = out.rsplit('STATUS:', 1)
        body = parts[0].strip()
        try: status = int(parts[1].strip())
        except: status = 0
        return status, body
    return 0, out

def deploy_fugr(name, source_file):
    """Deploy function group source."""
    print(f'=== {name} (FUGR) ===')
    status, cookie, csrf, etag = curl_get(f'/sap/bc/adt/functions/groups/{name.lower()}/source/main')
    print(f'  GET: {status}  csrf={bool(csrf)}  etag={etag[:20] if etag else "NONE"}')

    if status == 404:
        print(f'  FUGR not found, needs creation via SE37')
        return False

    with open(source_file, 'r', encoding='utf-8') as f:
        source = f.read()

    st, body = curl_put(
        f'/sap/bc/adt/functions/groups/{name.lower()}/source/main',
        source_file, 'text/plain; charset=utf-8', cookie, csrf, etag)
    print(f'  WRITE: {st}')
    if st not in (200, 201, 204):
        print(f'  ERR: {body[:300]}')
        return False
    print(f'  -> SOURCE WRITTEN')
    return True

def deploy_ddic_table(name, ddl_file):
    """Deploy DDIC table DDL source."""
    print(f'=== {name} (DDIC) ===')
    status, cookie, csrf, etag = curl_get(f'/sap/bc/adt/ddic/tables/{name.lower()}/source/main')
    print(f'  GET: {status}  csrf={bool(csrf)}  etag={etag[:20] if etag else "NONE"}')

    if status == 404:
        print(f'  Table not found, needs SE11 creation')
        return False

    if not os.path.exists(ddl_file):
        print(f'  DDL file not found: {ddl_file}')
        return False

    with open(ddl_file, 'r', encoding='utf-8') as f:
        source = f.read()

    # DDIC uses text/plain (DDL source)
    st, body = curl_put(
        f'/sap/bc/adt/ddic/tables/{name.lower()}/source/main',
        ddl_file, 'text/plain; charset=utf-8', cookie, csrf, etag)
    print(f'  WRITE: {st}')
    if st not in (200, 201, 204):
        print(f'  ERR: {body[:300]}')
        return False
    print(f'  -> SOURCE WRITTEN')
    return True

# ===== MAIN =====
results = []

# 1. YFG_SBDC function group
results.append(('YFG_SBDC', deploy_fugr('yfg_sbdc', str(DEPLOY_DIR / 'yfg_sbdc.fugr.abap'))))

# 2. DDIC tables - try DDL files first, then .tabl.abap
for table_name, ddl_file in [
    ('zrouter_config', 'zrouter_config.tabl.ddl'),
    ('zrouter_log', 'zrouter_log.tabl.ddl'),
    ('ysbdc_session', 'ysbdc_session.tabl.ddl'),
    ('ysbdc_result', 'ysbdc_result.tabl.ddl'),
    ('zrouter_template', 'zrouter_template.tabl.ddl'),
]:
    file_path = DEPLOY_DIR / ddl_file
    abap_path = DEPLOY_DIR / ddl_file.replace('.ddl', '.abap')
    if file_path.exists():
        results.append((table_name, deploy_ddic_table(table_name, str(file_path))))
    elif abap_path.exists():
        results.append((table_name, deploy_ddic_table(table_name, str(abap_path))))
    else:
        print(f'=== {table_name}: NO FILE FOUND ===')

# Summary
print()
print('=== DEPLOY SUMMARY ===')
for name, ok in results:
    print(f'  {name}: {"OK" if ok else "FAILED"}')
