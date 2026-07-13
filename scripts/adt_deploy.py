#!/usr/bin/env python3
"""Deploy ABAP source files to SAP via ADT REST API (curl, with ETag + CSRF)."""
import os
import subprocess

SAP_URL = os.environ.get("ARC_SAP_URL") or os.environ.get("SAP_URL")
SAP_USER = os.environ.get("ARC_SAP_USER") or os.environ.get("SAP_USER")
SAP_PASSWORD = os.environ.get("ARC_SAP_PASSWORD") or os.environ.get("SAP_PASSWORD")
if not SAP_URL or not SAP_USER or not SAP_PASSWORD:
    raise SystemExit("Missing ARC_SAP_URL/ARC_SAP_USER/ARC_SAP_PASSWORD for ADT deploy.")

CURL = ["curl", "-sS", "-u", f"{SAP_USER}:{SAP_PASSWORD}"]
if (os.environ.get("SAP_ALLOW_UNAUTHORIZED", "").lower() == "true"
        and os.environ.get("SAP_ENV", "").upper() not in {"PROD", "PRD", "PRODUCTION"}):
    CURL.insert(1, "-k")

def curl(method, path, data=None, content_type=None, cookie='', csrf='', etag=''):
    """Generic curl request. Returns (status_code, body)."""
    cmd = list(CURL)
    if method != 'GET':
        cmd += ['-X', method]
    if csrf:
        cmd += ['-H', 'x-csrf-token: ' + csrf]
    if content_type:
        cmd += ['-H', 'Content-Type: ' + content_type]
    if etag:
        cmd += ['-H', 'If-Match: ' + etag]
    if cookie:
        cmd += ['-b', cookie]
    if data:
        cmd += ['--data-binary', data]
    cmd += ['-w', '\nSTATUS:%{http_code}']
    cmd.append(SAP_URL + path)

    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    out = r.stdout
    if 'STATUS:' in out:
        parts = out.rsplit('STATUS:', 1)
        body = parts[0].strip()
        try:
            status = int(parts[1].strip())
        except ValueError:
            status = 0
        return status, body
    return 0, out

def curl_get(path):
    """GET with -i to parse headers. Returns (status, headers_dict, body, cookie, csrf)."""
    cmd = CURL + ['-i', '-H', 'x-csrf-token: fetch', SAP_URL + path]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    output = r.stdout

    sep = '\r\n\r\n' if '\r\n\r\n' in output else '\n\n'
    line_sep = '\r\n' if '\r\n\r\n' in output else '\n'

    parts = output.split(sep, 1)
    header_section = parts[0]
    body = parts[1] if len(parts) > 1 else ''

    headers = {}
    for line in header_section.split(line_sep):
        if ':' in line and not line.startswith('HTTP'):
            k, v = line.split(':', 1)
            headers[k.strip().lower()] = v.strip()

    status = 200
    first_line = header_section.split(line_sep)[0]
    if 'HTTP' in first_line:
        try:
            status = int(first_line.split()[1])
        except (IndexError, ValueError):
            pass

    csrf = headers.get('x-csrf-token', '')
    etag = headers.get('etag', '')
    cookie = ''
    for k, v in headers.items():
        if k == 'set-cookie' and 'sap_sessionid' in v.lower():
            for part in v.split(';'):
                part = part.strip()
                if 'sap_sessionid' in part.lower():
                    cookie = part
                    break

    return status, headers, body, cookie, csrf, etag

def deploy_class(name, source_file, package='$TMP'):
    print('=== Deploy {} ==='.format(name))

    # GET class metadata to get session
    status, _, _, cookie, csrf, _ = curl_get('/sap/bc/adt/oo/classes/' + name.lower())
    print('  GET class: {} csrf={}'.format(status, bool(csrf)))

    # GET source to get ETag
    st_src, _, _, cookie2, csrf2, etag = curl_get('/sap/bc/adt/oo/classes/' + name.lower() + '/source/main')
    c = cookie2 if cookie2 else cookie
    x = csrf2 if csrf2 else csrf
    print('  GET source: {} etag={}'.format(st_src, etag[:20] if etag else 'NONE'))

    if status == 404:
        create_xml = ('<?xml version="1.0" encoding="utf-8"?>'
            '<adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core">'
            '<adtcore:name>' + name.upper() + '</adtcore:name>'
            '<adtcore:type>CLAS/OC</adtcore:type>'
            '<adtcore:packageName>' + package + '</adtcore:packageName>'
            '</adtcore:objectReference>')
        st2, body2 = curl('POST', '/sap/bc/adt/oo/classes', create_xml, 'application/xml', c, x)
        print('  CREATE: {}'.format(st2))
        if st2 not in (200, 201):
            print('  CREATE ERR: {}'.format(body2[:300]))
            return False
        _, _, _, c, x, etag = curl_get('/sap/bc/adt/oo/classes/' + name.lower() + '/source/main')

    # Write source
    with open(source_file, 'r', encoding='utf-8') as f:
        source = f.read()

    st3, body3 = curl('PUT',
        '/sap/bc/adt/oo/classes/' + name.lower() + '/source/main',
        source, 'text/plain; charset=utf-8', c, x, etag)
    print('  WRITE: {}'.format(st3))
    if st3 not in (200, 201, 204):
        print('  WRITE err: {}'.format(body3[:400]))
        return False

    # NW 7.40: no ADT activation API — source written, activate manually
    # Attempt activation (works on 7.50+), ignore failure on 7.40
    _, _, _, c, x, etag = curl_get('/sap/bc/adt/oo/classes/' + name.lower() + '/source/main')
    act_xml = ('<?xml version="1.0" encoding="utf-8"?>'
        '<adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core">'
        '<adtcore:name>' + name.upper() + '</adtcore:name>'
        '<adtcore:type>CLAS/OC</adtcore:type>'
        '<adtcore:packageName>' + package + '</adtcore:packageName>'
        '</adtcore:objectReference>')
    st4, body4 = curl('POST',
        '/sap/bc/adt/activation/classes/' + name.lower(),
        act_xml, 'application/xml', c, x)
    print('  ACTIVATE: {} (404=NW7.40 expected, manual activate needed)'.format(st4))

    print('  -> SOURCE WRITTEN')
    return True

def deploy_program(name, source_file, package='$TMP'):
    print('=== Deploy {} (PROG) ==='.format(name))

    # GET program metadata
    status, _, _, cookie, csrf, _ = curl_get('/sap/bc/adt/programs/programs/' + name.lower())
    print('  GET prog: {} csrf={}'.format(status, bool(csrf)))

    # GET source to get ETag
    st_src, _, _, cookie2, csrf2, etag = curl_get('/sap/bc/adt/programs/programs/' + name.lower() + '/source/main')
    c = cookie2 if cookie2 else cookie
    x = csrf2 if csrf2 else csrf
    print('  GET source: {} etag={}'.format(st_src, etag[:20] if etag else 'NONE'))

    if status == 404:
        create_xml = ('<?xml version="1.0" encoding="utf-8"?>'
            '<adtcore:objectReference xmlns:adtcore="http://www.sap.com/adt/core">'
            '<adtcore:name>' + name.upper() + '</adtcore:name>'
            '<adtcore:type>PROG/P</adtcore:type>'
            '<adtcore:packageName>' + package + '</adtcore:packageName>'
            '</adtcore:objectReference>')
        st2, body2 = curl('POST', '/sap/bc/adt/programs/programs', create_xml, 'application/xml', c, x)
        print('  CREATE: {}'.format(st2))
        if st2 not in (200, 201):
            print('  CREATE ERR: {}'.format(body2[:300]))
            return False
        _, _, _, c, x, etag = curl_get('/sap/bc/adt/programs/programs/' + name.lower() + '/source/main')

    # Write source
    with open(source_file, 'r', encoding='utf-8') as f:
        source = f.read()

    st3, body3 = curl('PUT',
        '/sap/bc/adt/programs/programs/' + name.lower() + '/source/main',
        source, 'text/plain; charset=utf-8', c, x, etag)
    print('  WRITE: {}'.format(st3))
    if st3 not in (200, 201, 204):
        print('  WRITE err: {}'.format(body3[:400]))
        return False

    print('  -> SOURCE WRITTEN (activate manually in SE38)')
    return True


if __name__ == '__main__':
    deploy_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'deploy', 'split2')

    # Deploy all fixed files — skip activation (NW 7.40 has no ADT activation API)
    files = [
        ('zcl_zrouter_http', 'zcl_zrouter_http.clas.abap', 'class'),
        ('zcl_zrouter_logger', 'zcl_zrouter_logger.clas.abap', 'class'),
        ('zcl_zrouter_authority', 'zcl_zrouter_authority.clas.abap', 'class'),
        ('zreq', 'zreq.prog.abap', 'program'),
    ]

    for obj_name, file_name, obj_type in files:
        file_path = os.path.join(deploy_dir, file_name)
        if obj_type == 'class':
            ok = deploy_class(obj_name, file_path)
        else:
            ok = deploy_program(obj_name, file_path)
        print('{}: {}'.format(obj_name, 'OK' if ok else 'FAILED'))
        print()
