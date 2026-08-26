---
name: btp-admin
description: Administer SAP BTP through the btp-mcp-server MCP tools (subaccounts, directories, entitlements, environment instances, XSUAA role collections and roles). Use whenever the user asks to create, list, update, entitle, or delete anything in their BTP global account — e.g. "create a subaccount", "entitle a service", "set up a Cloud Foundry environment", "manage role collections". Explains which tool to pick, required payloads, and how to keep responses small.
---

# SAP BTP Administration via btp-mcp-server

This server exposes SAP BTP Core Services (CIS Accounts, Entitlements, Provisioning) and the XSUAA Authorization API as MCP tools. Tools follow the pattern `<EntitySet>_<operation>`, e.g. `Subaccounts_list`, `Assignments_update`, `EnvironmentInstances_create`.

## Tool selection map

| Task | Tool(s) |
|------|---------|
| Global account details / GUID | `GlobalAccount_list` |
| List, create, update, delete subaccounts | `Subaccounts_*` (key: `subaccountGUID`) |
| Group subaccounts into folders | `Directories_*` (key: `directoryGUID`) |
| See or change service entitlements | `Assignments_list`, `Assignments_update` |
| Valid regions for new subaccounts | `AllowedDataCenters_list` |
| Cloud Foundry orgs / Kyma runtimes | `EnvironmentInstances_*` (key: `environmentInstanceID`) |
| What environments can be provisioned | `AvailableEnvironments_list` |
| XSUAA app registrations (source of `appId`) | `Applications_list`, `Applications_get` |
| Role collections (assignable to users) | `RoleCollections_*` (key: `roleCollectionName`) |
| Roles from role templates | `Roles_*` (keys: `roleTemplateName`, `roleTemplateAppId`, `roleName`) |
| Role templates defined by apps | `RoleTemplates_*` (keys: `roleTemplateAppId`, `roleTemplateName`) |

Selection rules:

- "Entitle/assign a service or quota" → `Assignments_update`, never a create tool (Assignments has no create).
- "Create a Cloud Foundry org" → `EnvironmentInstances_create` with `environmentType: "cloudfoundry"` — CF orgs are environment instances, not subaccounts.
- "Give a user permissions" → work with **RoleCollections** (users are assigned role collections); Roles and RoleTemplates are only building blocks.
- When you already have a GUID/key, use the `_get` tool — never `_list` plus client-side scanning.

## Keep responses small (token discipline)

BTP list responses are verbose; an unfiltered `Assignments_list` or `Subaccounts_list` can return thousands of tokens of irrelevant fields. On every `_list` call:

1. **`$select`** only the fields you need (e.g. `$select=guid,displayName,region,state` for subaccounts).
2. **`$filter`** server-side instead of listing everything and scanning (e.g. `$filter=displayName eq 'dev'`).
3. **`$top`** when exploring (e.g. `$top=5`) — raise it only if needed.
4. Call `GlobalAccount_list` at most once per conversation and reuse the GUID.
5. Scope `Assignments_list` to one subaccount or directory — never fetch the full global entitlement tree unless explicitly asked.

## Payload shapes

### Create a subaccount (`Subaccounts_create`)

```json
{
  "displayName": "Dev",
  "subdomain": "myorg-dev",
  "region": "eu10",
  "description": "Development subaccount",
  "usedForProduction": "NOT_USED_FOR_PRODUCTION",
  "parentGUID": "<directory GUID, omit for global account root>"
}
```

- `displayName`, `subdomain`, `region` are required.
- `subdomain` must be unique within the region, lowercase, no spaces.
- Valid `region` values come from `AllowedDataCenters_list`.

### Entitle a service plan (`Assignments_update`)

```json
{
  "subaccountServicePlans": [
    {
      "serviceName": "hana-cloud",
      "servicePlanName": "hana",
      "assignmentInfo": [
        { "subaccountGUID": "<guid>", "amount": 1 }
      ]
    }
  ]
}
```

- Numeric-quota plans use `"amount": <n>` (set `0` to revoke).
- Boolean plans use `"enable": true` / `false` instead of `amount` — the two are mutually exclusive; sending both fails.
- The call is **asynchronous** (accepted, then processed) — verify with a scoped `Assignments_list` afterwards.

### Create a Cloud Foundry environment (`EnvironmentInstances_create`)

```json
{
  "environmentType": "cloudfoundry",
  "name": "my-org",
  "planName": "standard",
  "serviceName": "cloudfoundry",
  "landscapeLabel": "cf-eu10",
  "parameters": { "instance_name": "my-org" }
}
```

- Get valid `planName` and `landscapeLabel` values from `AvailableEnvironments_list` first.
- `parameters.instance_name` becomes the CF org name.
- Creation is asynchronous — poll `EnvironmentInstances_get` until `state` is `OK` (transient states: `CREATING`, `UPDATING`; `CREATION_FAILED` means inspect and report).

### Create a role collection (`RoleCollections_create`)

```json
{ "name": "Developer Support", "description": "Read access for support staff" }
```

### Roles (`Roles_*`)

Roles are identified by three keys, in this order: `roleTemplateName`, `roleTemplateAppId`, `roleName`. Get valid `roleTemplateAppId` values from `Applications_list` and template names from `RoleTemplates_list`.

## Common workflows

**Onboard a new subaccount with Cloud Foundry:**
1. `Subaccounts_create` → note the returned `guid` (wait for `state: OK` via `Subaccounts_get` if needed).
2. `Assignments_update` → entitle required service plans to that GUID.
3. `AvailableEnvironments_list` → pick plan + landscape.
4. `EnvironmentInstances_create` → create the CF org; poll `_get` until `OK`.

**Entitle a service to an existing subaccount:**
1. Resolve the subaccount GUID (`Subaccounts_list` with `$filter` on `displayName`).
2. `Assignments_update` with the payload above.
3. Confirm with `Assignments_list` scoped to that subaccount.

**Set up authorizations:**
1. `RoleCollections_create` for the new collection.
2. `RoleTemplates_list` / `Applications_list` to find the right template and app.
3. `Roles_create` / `RoleCollections_update` to wire roles into the collection.

## Pitfalls

- **Write operations are asynchronous.** Create/update/delete on subaccounts, entitlements, and environment instances return before completion. Never report success from the write response alone — confirm the final state with a follow-up `_get`/`_list` when the user needs certainty.
- **Deletes cascade.** Deleting a subaccount destroys its environments and data. Confirm with the user before any `_delete` call unless they explicitly asked for the deletion.
- **`amount` vs `enable`** on entitlements (see above) is the most common cause of failed `Assignments_update` calls.
- **Region ≠ landscape.** Subaccounts use `region` (e.g. `eu10`); environment instances use `landscapeLabel` (e.g. `cf-eu10`). Don't interchange them.
