// Catalogue of SAP API Management on-tenant Management.svc operations.
//
// Kept server-side so the tool surface stays small: agents call
// apim_search_actions to find an operation, then apim_execute_action to run it.
// Mutating entries are refused without an approval-broker grant.

const SVC = "/apiportal/api/1.0/Management.svc";

function odataQuote(value) {
  return String(value).replace(/'/g, "''");
}

function keyed(entitySet, key) {
  return `${SVC}/${entitySet}('${encodeURIComponent(odataQuote(key))}')`;
}

export const ACTIONS = [
  {
    id: "proxies.list",
    summary: "List API proxies on the tenant.",
    entity: "APIProxies",
    mutating: false,
    params: { top: "optional max rows", filter: "optional OData $filter", select: "optional $select" },
    build: ({ top, filter, select } = {}) => {
      const query = new URLSearchParams({ $format: "json" });
      if (top) query.set("$top", String(top));
      if (filter) query.set("$filter", String(filter));
      if (select) query.set("$select", String(select));
      return { method: "GET", path: `${SVC}/APIProxies?${query}` };
    },
  },
  {
    id: "proxies.get",
    summary: "Read one API proxy's metadata.",
    entity: "APIProxies",
    mutating: false,
    params: { name: "proxy name (required)" },
    build: ({ name }) => ({ method: "GET", path: `${keyed("APIProxies", name)}?$format=json` }),
  },
  {
    id: "proxies.export",
    summary: "Download an API proxy bundle ZIP ($value).",
    entity: "APIProxies",
    mutating: false,
    params: { name: "proxy name (required)" },
    build: ({ name }) => ({ method: "GET", path: `${keyed("APIProxies", name)}/$value` }),
  },
  {
    id: "proxies.import",
    summary: "Upload/replace an API proxy bundle ZIP ($value). Mutating.",
    entity: "APIProxies",
    mutating: true,
    capability: "sap.apim.proxy.deploy",
    params: { name: "proxy name (required)", bundle: "path to the proxy ZIP (required)" },
    build: ({ name }) => ({ method: "PUT", path: `${keyed("APIProxies", name)}/$value`, contentType: "application/zip" }),
  },
  {
    id: "proxies.delete",
    summary: "Delete an API proxy. Mutating.",
    entity: "APIProxies",
    mutating: true,
    capability: "sap.apim.proxy.modify",
    params: { name: "proxy name (required)" },
    build: ({ name }) => ({ method: "DELETE", path: keyed("APIProxies", name) }),
  },
  {
    id: "products.list",
    summary: "List API products.",
    entity: "APIProducts",
    mutating: false,
    params: { top: "optional max rows", filter: "optional OData $filter" },
    build: ({ top, filter } = {}) => {
      const query = new URLSearchParams({ $format: "json" });
      if (top) query.set("$top", String(top));
      if (filter) query.set("$filter", String(filter));
      return { method: "GET", path: `${SVC}/APIProducts?${query}` };
    },
  },
  {
    id: "products.get",
    summary: "Read one API product.",
    entity: "APIProducts",
    mutating: false,
    params: { name: "product name (required)" },
    build: ({ name }) => ({ method: "GET", path: `${keyed("APIProducts", name)}?$format=json` }),
  },
  {
    id: "products.create",
    summary: "Create an API product from a JSON payload. Mutating.",
    entity: "APIProducts",
    mutating: true,
    capability: "sap.apim.proxy.modify",
    params: { payload: "product JSON body (required)" },
    build: () => ({ method: "POST", path: `${SVC}/APIProducts`, contentType: "application/json" }),
  },
  {
    id: "providers.list",
    summary: "List API providers (backend systems).",
    entity: "APIProviders",
    mutating: false,
    params: { top: "optional max rows" },
    build: ({ top } = {}) => {
      const query = new URLSearchParams({ $format: "json" });
      if (top) query.set("$top", String(top));
      return { method: "GET", path: `${SVC}/APIProviders?${query}` };
    },
  },
  {
    id: "applications.list",
    summary: "List developer applications (API key holders).",
    entity: "Applications",
    mutating: false,
    params: { top: "optional max rows", filter: "optional OData $filter" },
    build: ({ top, filter } = {}) => {
      const query = new URLSearchParams({ $format: "json" });
      if (top) query.set("$top", String(top));
      if (filter) query.set("$filter", String(filter));
      return { method: "GET", path: `${SVC}/Applications?${query}` };
    },
  },
  {
    id: "kvm.list",
    summary: "List Key Value Maps.",
    entity: "KeyMapEntries",
    mutating: false,
    params: { top: "optional max rows" },
    build: ({ top } = {}) => {
      const query = new URLSearchParams({ $format: "json" });
      if (top) query.set("$top", String(top));
      return { method: "GET", path: `${SVC}/KeyMapEntries?${query}` };
    },
  },
  {
    id: "kvm.get",
    summary: "Read one Key Value Map and its entries.",
    entity: "KeyMapEntries",
    mutating: false,
    params: { name: "KVM name (required)" },
    build: ({ name }) => ({ method: "GET", path: `${keyed("KeyMapEntries", name)}?$expand=keyMapEntryValues&$format=json` }),
  },
  {
    id: "kvm.create",
    summary: "Create a Key Value Map from a JSON payload. Mutating.",
    entity: "KeyMapEntries",
    mutating: true,
    capability: "sap.apim.proxy.modify",
    params: { payload: "KVM JSON body (required)" },
    build: () => ({ method: "POST", path: `${SVC}/KeyMapEntries`, contentType: "application/json" }),
  },
  {
    id: "metadata",
    summary: "Fetch the Management.svc OData metadata document.",
    entity: "$metadata",
    mutating: false,
    params: {},
    build: () => ({ method: "GET", path: `${SVC}/$metadata` }),
  },
];

const BY_ID = new Map(ACTIONS.map((action) => [action.id, action]));

export function getAction(id) {
  return BY_ID.get(id) || null;
}

/**
 * Fold simple plurals so "proxy" finds "APIProxies" and "products" finds "product".
 * Crude on purpose: the catalogue is small and an agent's query is rarely exotic.
 */
function singularize(word) {
  if (word.endsWith("ies") && word.length > 4) {
    return `${word.slice(0, -3)}y`;
  }
  if (word.endsWith("ss")) {
    return word;
  }
  if (word.endsWith("s") && word.length > 3) {
    return word.slice(0, -1);
  }
  return word;
}

function stemmed(text) {
  return text.split(/[^a-z0-9]+/).map(singularize).join(" ");
}

export function searchActions(query, { includeMutating = true } = {}) {
  const terms = String(query || "")
    .toLowerCase()
    .split(/\s+/)
    .filter(Boolean);
  const scored = ACTIONS.filter((action) => includeMutating || !action.mutating).map((action) => {
    const haystack = `${action.id} ${action.summary} ${action.entity}`.toLowerCase();
    const haystackStem = stemmed(haystack);
    const score =
      terms.length === 0
        ? 1
        : terms.filter((term) => haystack.includes(term) || haystackStem.includes(singularize(term))).length;
    return { action, score };
  });
  return scored
    .filter((entry) => entry.score > 0)
    .sort((a, b) => b.score - a.score)
    .map(({ action }) => ({
      id: action.id,
      summary: action.summary,
      entity: action.entity,
      mutating: action.mutating,
      capability: action.capability || null,
      params: action.params,
    }));
}
