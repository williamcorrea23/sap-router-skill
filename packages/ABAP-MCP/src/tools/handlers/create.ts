/**
 * CREATE tool handlers: all 7 create_* tools
 */

import type { ADTClient } from "abap-adt-api";
import type { ToolResult } from "../../types.js";
import { S_CreateProgram, S_CreateClass, S_CreateInterface, S_CreateFunctionGroup, S_CreateCdsView, S_CreateTable, S_CreateMessageClass, S_CreateCdsMetadataExtension, S_CreateServiceDefinition, S_CreateServiceBinding, S_PublishServiceBinding, S_CreateDataControlLanguage, S_CreateBehaviorDefinition, S_CreatePackage } from "../../schemas.js";
import { ADT_PACKAGES, ADT_PROGRAMS, ADT_CLASSES, ADT_INTERFACES, ADT_FUNCTION_GROUPS, ADT_DDIC_DDL_SOURCES, ADT_DDIC_TABLES, ADT_DDIC_DDLX_SOURCES, ADT_DDIC_SRVD_SOURCES, ADT_BUSINESSSERVICES_BINDINGS, ADT_ACM_DCL_SOURCES, ADT_BO_BEHAVIORS } from "../../adt-endpoints.js";

const encXml = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
import { assertWriteEnabled, assertPackageAllowed, assertCustomerNamespace } from "../../safety.js";
import * as fs from "fs";

function ok(text: string): ToolResult { return { content: [{ type: "text", text }] }; }

export async function handleCreateAbapProgram(client: ADTClient, args: Record<string, unknown>): Promise<ToolResult> {
  assertWriteEnabled();
  const p = S_CreateProgram.parse(args);
  assertPackageAllowed(p.devClass);
  assertCustomerNamespace(p.name, ["Z", "Y"]);
  const n = p.name.toUpperCase();
  const progType = p.programType ?? "P";
  await client.createObject(`PROG/${progType}`, n, p.devClass, p.description, `${ADT_PACKAGES}/${encodeURIComponent(p.devClass)}`, undefined, p.transport || undefined);
  const url = `${ADT_PROGRAMS}/${n.toLowerCase()}`;
  const label = progType === "I" ? "Include" : "Program";
  return ok(`✅ ${label} '${n}' created\nURI: ${url}\n\nNext steps:\n  write_abap_source with objectUrl='${url}'`);
}

export async function handleCreateAbapClass(client: ADTClient, args: Record<string, unknown>): Promise<ToolResult> {
  assertWriteEnabled();
  const p = S_CreateClass.parse(args);
  assertPackageAllowed(p.devClass);
  assertCustomerNamespace(p.name, ["ZCL_", "YCL_", "ZBP_", "YBP_"]);
  const n = p.name.toUpperCase();
  const url = `${ADT_CLASSES}/${n.toLowerCase()}`;
  const classCategory = p.classCategory ?? "generalObjectType";
  const responsible = client.httpClient.username.toUpperCase();

  // For behaviorPool classes, use a direct HTTP POST with class:category attribute.
  // client.createObject() does not support setting the class category.
  if (classCategory === "behaviorPool") {
    const body = [
      `<?xml version="1.0" encoding="UTF-8"?>`,
      `<class:abapClass xmlns:class="http://www.sap.com/adt/oo/classes"`,
      `  xmlns:adtcore="http://www.sap.com/adt/core"`,
      `  adtcore:description="${encXml(p.description)}"`,
      `  adtcore:name="${n}" adtcore:type="CLAS/OC"`,
      `  adtcore:language="EN" adtcore:masterLanguage="EN"`,
      `  adtcore:responsible="${responsible}"`,
      `  class:category="behaviorPool"`,
      `  class:final="true" class:abstract="true" class:visibility="public">`,
      `  <adtcore:packageRef adtcore:name="${p.devClass}"/>`,
      `</class:abapClass>`,
    ].join("\n");
    const qs: Record<string, string> = {};
    if (p.transport) qs.corrNr = p.transport;
    try {
      await client.httpClient.request(ADT_CLASSES, { method: "POST", headers: { "Content-Type": "application/*" }, qs, body });
    } catch (createErr) {
      const errMsg = createErr instanceof Error ? createErr.message : String(createErr);
      if (errMsg.includes("already exist") || errMsg.includes("SADT_RESOURCE/1")) throw createErr;
      try {
        await client.objectStructure(url);
        return ok(`✅ Class '${n}' created as behaviorPool (ADT returned a non-fatal error: ${errMsg.substring(0, 120)})\nURI: ${url}\n\nNext steps:\n  read_abap_source → write_abap_source`);
      } catch { throw createErr; }
    }
    return ok(`✅ Class '${n}' created as behaviorPool\nURI: ${url}\n\nNext steps:\n  read_abap_source → write_abap_source`);
  }

  try {
    await client.createObject("CLAS/OC", n, p.devClass, p.description, `${ADT_PACKAGES}/${encodeURIComponent(p.devClass)}`, undefined, p.transport || undefined);
  } catch (createErr) {
    // ADT sometimes returns a non-2xx response even when the class was successfully created
    // (e.g. HTTP 500 with a redirect or warning body). Verify by checking if the object exists.
    const errMsg = createErr instanceof Error ? createErr.message : String(createErr);
    // "already exist" / SADT_RESOURCE/1 = genuine duplicate — propagate, don't treat as false-success.
    if (errMsg.includes("already exist") || errMsg.includes("SADT_RESOURCE/1")) {
      throw createErr;
    }
    try {
      await client.objectStructure(url);
      // Object exists → creation succeeded despite the error response (e.g. HTTP 500 + warning body)
      return ok(
        `✅ Class '${n}' created (ADT returned a non-fatal error: ${errMsg.substring(0, 120)})\n` +
        `URI: ${url}\n\nNext steps:\n  read_abap_source → write_abap_source`
      );
    } catch {
      // Object does not exist → real failure
      throw createErr;
    }
  }
  // createObject cannot set a superclass — be explicit instead of silently
  // dropping the parameter, so the caller knows to add the inheritance.
  const superClassNote = p.superClass
    ? `\n\n⚠️ Note: superClass='${p.superClass}' is NOT applied at creation (ADT limitation). ` +
      `Add 'INHERITING FROM ${p.superClass.toUpperCase()}' to the class definition via write_abap_source.`
    : "";
  return ok(`✅ Class '${n}' created\nURI: ${url}${superClassNote}\n\nNext steps:\n  read_abap_source → write_abap_source`);
}

export async function handleCreateAbapInterface(client: ADTClient, args: Record<string, unknown>): Promise<ToolResult> {
  assertWriteEnabled();
  const p = S_CreateInterface.parse(args);
  assertPackageAllowed(p.devClass);
  assertCustomerNamespace(p.name, ["ZIF_", "YIF_"]);
  const n = p.name.toUpperCase();
  await client.createObject("INTF/OI", n, p.devClass, p.description, `${ADT_PACKAGES}/${encodeURIComponent(p.devClass)}`, undefined, p.transport || undefined);
  const url = `${ADT_INTERFACES}/${n.toLowerCase()}`;
  return ok(`✅ Interface '${n}' created\nURI: ${url}`);
}

export async function handleCreateFunctionGroup(client: ADTClient, args: Record<string, unknown>): Promise<ToolResult> {
  assertWriteEnabled();
  const p = S_CreateFunctionGroup.parse(args);
  assertPackageAllowed(p.devClass);
  assertCustomerNamespace(p.name, ["Z", "Y"]);
  const n = p.name.toUpperCase();
  await client.createObject("FUGR/F", n, p.devClass, p.description, `${ADT_PACKAGES}/${encodeURIComponent(p.devClass)}`, undefined, p.transport || undefined);
  const url = `${ADT_FUNCTION_GROUPS}/${n.toLowerCase()}`;
  return ok(`✅ Function group '${n}' created\nURI: ${url}`);
}

export async function handleCreateCdsView(client: ADTClient, args: Record<string, unknown>): Promise<ToolResult> {
  assertWriteEnabled();
  const p = S_CreateCdsView.parse(args);
  assertPackageAllowed(p.devClass);
  assertCustomerNamespace(p.name, ["Z", "Y"]);
  const n = p.name.toUpperCase();
  const url = `${ADT_DDIC_DDL_SOURCES}/${n.toLowerCase()}`;
  const responsible = client.httpClient.username.toUpperCase();

  // Resolve initial source from inline string or file path.
  // On some S/4HANA on-premise systems the DDL sources endpoint requires the
  // CDS source code to be embedded in the creation request body as a
  // <ddlSource:ddlSource> child element — omitting it causes a T100 validation
  // error "System expected the element ddlSource".
  let initialSource: string | undefined;
  if (p.sourcePath) {
    try {
      initialSource = fs.readFileSync(p.sourcePath, "utf-8");
    } catch (e) {
      throw new Error(`Cannot read sourcePath '${p.sourcePath}': ${e instanceof Error ? e.message : String(e)}`);
    }
  } else if (p.source) {
    initialSource = p.source;
  }

  // abap-adt-api's createObject does not pass corrNr correctly for DDLS objects.
  // Use direct HTTP POST to guarantee corrNr is included.
  // The root element for DDLS/DF MUST be ddl:ddlSource (namespace http://www.sap.com/adt/ddic/ddlsources),
  // NOT blue:blueSource. S/4HANA on-premise systems additionally require the CDS source code to be
  // embedded inline as a CDATA text node of the root element.
  // "]]>" inside the source would terminate the CDATA section early and break
  // the XML — split it across two CDATA sections (standard escaping technique).
  const sourceBody = initialSource
    ? `<![CDATA[${initialSource.replace(/\]\]>/g, "]]]]><![CDATA[>")}]]>`
    : "";

  const body = [
    `<?xml version="1.0" encoding="UTF-8"?>`,
    `<ddl:ddlSource xmlns:ddl="http://www.sap.com/adt/ddic/ddlsources"`,
    `  xmlns:adtcore="http://www.sap.com/adt/core"`,
    `  adtcore:description="${encXml(p.description)}"`,
    `  adtcore:name="${n}" adtcore:type="DDLS/DF"`,
    `  adtcore:language="EN" adtcore:masterLanguage="EN"`,
    `  adtcore:responsible="${responsible}">`,
    `  <adtcore:packageRef adtcore:name="${p.devClass}"/>${sourceBody}`,
    `</ddl:ddlSource>`,
  ].join("\n");

  const qs: Record<string, string> = {};
  if (p.transport) qs.corrNr = p.transport;

  try {
    await client.httpClient.request(ADT_DDIC_DDL_SOURCES, {
      method: "POST",
      headers: { "Content-Type": "application/*" },
      qs,
      body,
    });
  } catch (createErr) {
    const errMsg = createErr instanceof Error ? createErr.message : String(createErr);
    if (errMsg.includes("already exist") || errMsg.includes("SADT_RESOURCE/1")) {
      throw createErr;
    }
    try {
      await client.objectStructure(url);
      return ok(`✅ CDS View '${n}' created (ADT returned a non-fatal error: ${errMsg.substring(0, 120)})\nURI: ${url}`);
    } catch {
      throw createErr;
    }
  }

  return ok(`✅ CDS View '${n}' created\nURI: ${url}\n\nNext step:\n  write_abap_source with objectUrl='${url}' to update the source`);
}

export async function handleCreateDatabaseTable(client: ADTClient, args: Record<string, unknown>): Promise<ToolResult> {
  assertWriteEnabled();
  const p = S_CreateTable.parse(args);
  assertPackageAllowed(p.devClass);
  assertCustomerNamespace(p.name, ["Z", "Y"]);
  const n = p.name.toUpperCase();
  const url = `${ADT_DDIC_TABLES}/${n.toLowerCase()}`;

  // abap-adt-api's createObject passes corrNr as a query param, but the ADT endpoint
  // for TABL/DT requires it to be present. Use a direct HTTP POST (same pattern as
  // handleCreateBehaviorDefinition) to guarantee corrNr is always included.
  const responsible = client.httpClient.username.toUpperCase();
  const body = [
    `<?xml version="1.0" encoding="UTF-8"?>`,
    `<blue:blueSource xmlns:blue="http://www.sap.com/wbobj/blue"`,
    `  xmlns:adtcore="http://www.sap.com/adt/core"`,
    `  adtcore:description="${encXml(p.description)}"`,
    `  adtcore:name="${n}" adtcore:type="TABL/DT"`,
    `  adtcore:language="EN" adtcore:masterLanguage="EN"`,
    `  adtcore:responsible="${responsible}">`,
    `  <adtcore:packageRef adtcore:name="${p.devClass}"/>`,
    `</blue:blueSource>`,
  ].join("\n");

  const qs: Record<string, string> = {};
  if (p.transport) qs.corrNr = p.transport;

  try {
    await client.httpClient.request(ADT_DDIC_TABLES, {
      method: "POST",
      headers: { "Content-Type": "application/*" },
      qs,
      body,
    });
  } catch (createErr) {
    // Verify whether the table was actually created despite a non-2xx response
    const errMsg = createErr instanceof Error ? createErr.message : String(createErr);
    // "already exist" / SADT_RESOURCE/1 = genuine duplicate — propagate, don't treat as false-success.
    if (errMsg.includes("already exist") || errMsg.includes("SADT_RESOURCE/1")) {
      throw createErr;
    }
    try {
      await client.objectStructure(url);
      return ok(`✅ Table '${n}' created (ADT returned a non-fatal error: ${errMsg.substring(0, 120)})\nURI: ${url}`);
    } catch {
      throw createErr;
    }
  }

  return ok(`✅ Table '${n}' created\nURI: ${url}`);
}

export async function handleCreateMessageClass(client: ADTClient, args: Record<string, unknown>): Promise<ToolResult> {
  assertWriteEnabled();
  const p = S_CreateMessageClass.parse(args);
  assertPackageAllowed(p.devClass);
  assertCustomerNamespace(p.name, ["Z", "Y"]);
  const n = p.name.toUpperCase();
  await client.createObject("MSAG/N", n, p.devClass, p.description, `${ADT_PACKAGES}/${encodeURIComponent(p.devClass)}`, undefined, p.transport || undefined);
  return ok(`✅ Message class '${n}' created`);
}

export async function handleCreateCdsMetadataExtension(client: ADTClient, args: Record<string, unknown>): Promise<ToolResult> {
  assertWriteEnabled();
  const p = S_CreateCdsMetadataExtension.parse(args);
  assertPackageAllowed(p.devClass);
  assertCustomerNamespace(p.name, ["Z", "Y"]);
  const n = p.name.toUpperCase();
  await client.createObject("DDLX/EX", n, p.devClass, p.description, `${ADT_PACKAGES}/${encodeURIComponent(p.devClass)}`, undefined, p.transport || undefined);
  const url = `${ADT_DDIC_DDLX_SOURCES}/${n.toLowerCase()}`;
  return ok(`✅ CDS Metadata Extension '${n}' created\nURI: ${url}\n\nNext step:\n  write_abap_source with objectUrl='${url}'`);
}

export async function handleCreateServiceDefinition(client: ADTClient, args: Record<string, unknown>): Promise<ToolResult> {
  assertWriteEnabled();
  const p = S_CreateServiceDefinition.parse(args);
  assertPackageAllowed(p.devClass);
  assertCustomerNamespace(p.name, ["Z", "Y"]);
  const n = p.name.toUpperCase();
  await client.createObject("SRVD/SRV", n, p.devClass, p.description, `${ADT_PACKAGES}/${encodeURIComponent(p.devClass)}`, undefined, p.transport || undefined);
  const url = `${ADT_DDIC_SRVD_SOURCES}/${n.toLowerCase()}`;
  return ok(`✅ Service Definition '${n}' created\nURI: ${url}\n\nNext steps:\n  1. write_abap_source with objectUrl='${url}'\n  2. create_service_binding to expose it as OData`);
}

export async function handleCreateServiceBinding(client: ADTClient, args: Record<string, unknown>): Promise<ToolResult> {
  assertWriteEnabled();
  const p = S_CreateServiceBinding.parse(args);
  assertPackageAllowed(p.devClass);
  assertCustomerNamespace(p.name, ["Z", "Y"]);
  const n = p.name.toUpperCase();
  const responsible = client.httpClient.username.toUpperCase();
  const svc = p.serviceDefinition.toUpperCase();

  // The binding type is encoded by TWO orthogonal attributes on <srvb:binding>:
  //   srvb:version  = "V2" | "V4"  (OData protocol version)
  //   srvb:category = "0"  | "1"   ("0" = Web API, "1" = UI)
  // (verified against a live V4 Web API binding: type="ODATA" version="V4" category="0").
  // abap-adt-api's createObject hardcodes version="V2" category="0" in
  // objectcreator.createBodyBinding, so it can ONLY ever create an OData V2
  // binding — the requested category is silently dropped. We therefore build the
  // ADT create payload ourselves and POST it directly, mirroring createObject's
  // URL/headers/transport handling (same pattern as create_behavior_definition).
  const odataVersion = p.bindingType.startsWith("V4") ? "V4" : "V2";
  const category = p.bindingType.endsWith("_UI") ? "1" : "0";

  const body = [
    `<?xml version="1.0" encoding="UTF-8"?>`,
    `<srvb:serviceBinding xmlns:srvb="http://www.sap.com/adt/ddic/ServiceBindings"`,
    `  xmlns:adtcore="http://www.sap.com/adt/core"`,
    `  adtcore:description="${encXml(p.description)}"`,
    `  adtcore:name="${n}" adtcore:type="SRVB/SVB"`,
    `  adtcore:language="EN" adtcore:masterLanguage="EN"`,
    `  adtcore:responsible="${responsible}">`,
    `  <adtcore:packageRef adtcore:name="${p.devClass}"/>`,
    `  <srvb:services srvb:name="${n}">`,
    `    <srvb:content srvb:version="0001">`,
    `      <srvb:serviceDefinition adtcore:name="${svc}"/>`,
    `    </srvb:content>`,
    `  </srvb:services>`,
    `  <srvb:binding srvb:type="ODATA" srvb:version="${odataVersion}" srvb:category="${category}">`,
    `    <srvb:implementation adtcore:name=""/>`,
    `  </srvb:binding>`,
    `</srvb:serviceBinding>`,
  ].join("\n");

  const qs: Record<string, string> = {};
  if (p.transport) qs.corrNr = p.transport;

  await client.httpClient.request(ADT_BUSINESSSERVICES_BINDINGS, {
    method: "POST",
    headers: { "Content-Type": "application/*" },
    qs,
    body,
  });

  const url = `${ADT_BUSINESSSERVICES_BINDINGS}/${n.toLowerCase()}`;
  return ok(`✅ Service Binding '${n}' created (${p.bindingType} → OData ${odataVersion}, category ${category})\nService Definition: ${svc}\nURI: ${url}\n\nNext step:\n  publish_service_binding with name='${n}'`);
}

export async function handlePublishServiceBinding(client: ADTClient, args: Record<string, unknown>): Promise<ToolResult> {
  assertWriteEnabled();
  const p = S_PublishServiceBinding.parse(args);
  const n = p.name.toUpperCase();
  const version = p.version ?? "0001";

  // abap-adt-api's publishServiceBinding hardcodes the OData *V2* publish-job
  // endpoint (/businessservices/odatav2/publishjobs), so it silently fails to
  // register a V4 binding's service group. It also only treats severity "E"/"A"
  // as failure, but the backend returns the full word "ERROR" — so real failures
  // (e.g. "Publishing in Customizing Client not allowed") were reported as success
  // with an undefined message. We detect the binding's protocol and POST the
  // publish job to the matching endpoint ourselves, then parse the result robustly.
  let protocol: "odatav2" | "odatav4" = "odatav2";
  try {
    const info = await client.httpClient.request(`${ADT_BUSINESSSERVICES_BINDINGS}/${n.toLowerCase()}`, {
      headers: { Accept: "application/vnd.sap.adt.businessservices.servicebinding.v2+xml" },
    });
    if (/srvb:version="V4"/.test(info.body)) protocol = "odatav4";
  } catch {
    // Binding not readable — fall back to odatav2 (legacy default).
  }

  const body =
    `<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">` +
    `<adtcore:objectReference adtcore:name="${n}"/>` +
    `</adtcore:objectReferences>`;
  const url =
    `/sap/bc/adt/businessservices/${protocol}/publishjobs` +
    `?servicename=${encodeURIComponent(n)}&serviceversion=${version}`;

  const resp = await client.httpClient.request(url, {
    method: "POST",
    headers: { Accept: "application/*", "Content-Type": "application/*" },
    body,
  });

  const pick = (tag: string) => new RegExp(`<${tag}>([^<]*)</${tag}>`).exec(resp.body)?.[1] ?? "";
  const severity = pick("SEVERITY");
  const shortText = pick("SHORT_TEXT");
  const longText = pick("LONG_TEXT");

  if (/^(E|A|ERROR|ABORT)$/i.test(severity)) {
    return { content: [{ type: "text", text: `❌ Publish failed (${severity}) via ${protocol}: ${shortText}${longText ? "\n" + longText : ""}` }] };
  }
  return ok(`✅ Service Binding '${n}' published via ${protocol}${shortText ? "\n" + shortText : ""}${longText ? "\n" + longText : ""}`);
}

export async function handleCreateDataControlLanguage(client: ADTClient, args: Record<string, unknown>): Promise<ToolResult> {
  assertWriteEnabled();
  const p = S_CreateDataControlLanguage.parse(args);
  assertPackageAllowed(p.devClass);
  assertCustomerNamespace(p.name, ["Z", "Y"]);
  const n = p.name.toUpperCase();
  await client.createObject("DCLS/DL", n, p.devClass, p.description, `${ADT_PACKAGES}/${encodeURIComponent(p.devClass)}`, undefined, p.transport || undefined);
  const url = `${ADT_ACM_DCL_SOURCES}/${n.toLowerCase()}`;
  return ok(`✅ Data Control Language source '${n}' created\nURI: ${url}\n\nNext step:\n  write_abap_source with objectUrl='${url}'`);
}

export async function handleCreateBehaviorDefinition(client: ADTClient, args: Record<string, unknown>): Promise<ToolResult> {
  assertWriteEnabled();
  const p = S_CreateBehaviorDefinition.parse(args);
  assertPackageAllowed(p.devClass);
  assertCustomerNamespace(p.name, ["Z", "Y"]);
  const n = p.name.toUpperCase();
  const responsible = client.httpClient.username.toUpperCase();

  // abap-adt-api has no BDEF support — direct HTTP POST to /sap/bc/adt/bo/behaviordefinitions
  // The endpoint expects the standard blue:blueSource format (same as TABL/DDLS), type BDEF/BDO
  const body = [
    `<?xml version="1.0" encoding="UTF-8"?>`,
    `<blue:blueSource xmlns:blue="http://www.sap.com/wbobj/blue"`,
    `  xmlns:adtcore="http://www.sap.com/adt/core"`,
    `  adtcore:description="${encXml(p.description)}"`,
    `  adtcore:name="${n}" adtcore:type="BDEF/BDO"`,
    `  adtcore:language="EN" adtcore:masterLanguage="EN"`,
    `  adtcore:responsible="${responsible}">`,
    `  <adtcore:packageRef adtcore:name="${p.devClass}"/>`,
    `</blue:blueSource>`,
  ].join("\n");

  const qs: Record<string, string> = {};
  if (p.transport) qs.corrNr = p.transport;

  await client.httpClient.request(ADT_BO_BEHAVIORS, {
    method: "POST",
    headers: { "Content-Type": "application/*" },
    qs,
    body,
  });

  const url = `${ADT_BO_BEHAVIORS}/${n.toLowerCase()}`;
  return ok(
    `✅ Behavior Definition '${n}' created\nURI: ${url}\n\n` +
    `Next steps:\n` +
    `  1. write_abap_source with objectUrl='${url}'\n` +
    `     First line must be: managed; | unmanaged; | projection; | abstract; | interface;\n` +
    `  2. Use the rap-bdef skill for full BDL syntax`
  );
}

export async function handleCreatePackage(client: ADTClient, args: Record<string, unknown>): Promise<ToolResult> {
  assertWriteEnabled();
  const p = S_CreatePackage.parse(args);
  assertPackageAllowed(p.name);
  assertCustomerNamespace(p.name, ["Z", "Y"]);
  const n = p.name.toUpperCase();
  const responsible = client.httpClient.username.toUpperCase();
  const swComp = (p.softwareComponent ?? "HOME").toUpperCase();
  const pkgType = p.packageType ?? "development";
  const isLocal = swComp === "LOCAL";

  // abap-adt-api's createObject DOES support DEVC/K, but createBodyPackage hardcodes
  // <adtcore:packageRef adtcore:name="YMU_RAP"/> (a leftover bug), so we build the
  // <pak:package> payload ourselves and POST it directly — same pattern as the
  // table/binding/BDEF handlers. A transportable package uses softwareComponent="HOME"
  // (+ optional transport layer / corrNr); a local, non-transportable package uses
  // softwareComponent="LOCAL" and no transport layer.
  const superPkg = p.superPackage
    ? `<pak:superPackage adtcore:name="${encXml(p.superPackage.toUpperCase())}"/>`
    : `<pak:superPackage/>`;
  // The ADT packages endpoint requires the <pak:transportLayer> element to always
  // be present. An empty pak:name selects the "Local Developments (No Transport)"
  // layer; a transportable package needs a real layer (e.g. Z<SID>).
  const layerName = isLocal ? "" : (p.transportLayer ? p.transportLayer.toUpperCase() : "");

  const body = [
    `<?xml version="1.0" encoding="UTF-8"?>`,
    `<pak:package xmlns:pak="http://www.sap.com/adt/packages"`,
    `  xmlns:adtcore="http://www.sap.com/adt/core"`,
    `  adtcore:description="${encXml(p.description)}"`,
    `  adtcore:name="${n}" adtcore:type="DEVC/K" adtcore:version="active"`,
    `  adtcore:language="EN" adtcore:masterLanguage="EN"`,
    `  adtcore:responsible="${responsible}">`,
    `  <pak:attributes pak:packageType="${encXml(pkgType)}"/>`,
    `  ${superPkg}`,
    `  <pak:applicationComponent/>`,
    `  <pak:transport>`,
    `    <pak:softwareComponent pak:name="${encXml(swComp)}"/>`,
    `    <pak:transportLayer pak:name="${encXml(layerName)}"/>`,
    `  </pak:transport>`,
    `  <pak:translation/>`,
    `  <pak:useAccesses/>`,
    `  <pak:packageInterfaces/>`,
    `  <pak:subPackages/>`,
    `</pak:package>`,
  ].join("\n");

  const qs: Record<string, string> = {};
  if (!isLocal && p.transport) qs.corrNr = p.transport;

  const url = `${ADT_PACKAGES}/${encodeURIComponent(n.toLowerCase())}`;

  try {
    await client.httpClient.request(ADT_PACKAGES, {
      method: "POST",
      headers: { "Content-Type": "application/*" },
      qs,
      body,
    });
  } catch (createErr) {
    const errMsg = createErr instanceof Error ? createErr.message : String(createErr);
    if (errMsg.includes("already exist") || errMsg.includes("SADT_RESOURCE/1")) {
      throw createErr;
    }
    // ADT sometimes returns a non-2xx response even when the package was created.
    try {
      await client.objectStructure(url);
      return ok(`✅ Package '${n}' created (ADT returned a non-fatal error: ${errMsg.substring(0, 120)})\nURI: ${url}`);
    } catch {
      throw createErr;
    }
  }

  const kind = isLocal ? "local (non-transportable)" : "transportable";
  return ok(`✅ Package '${n}' created — ${kind}, software component ${swComp}\nURI: ${url}\n\nNext step:\n  create objects with devClass='${n}'`);
}
