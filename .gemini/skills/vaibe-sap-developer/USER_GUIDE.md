# Using the vaibe-sap-developer Skill

A quick guide to actually using this skill — no internals, just what to expect and what to have ready.

## What it does
Generates Clean Core-compliant SAP ABAP code: CDS views, AMDP, RAP business objects, OData/Fiori exposure, IDoc retrigger/enhancement, Function Modules, BAdIs, classic ALV/Dynpro/WebDynpro (legacy only), Forms, Workflow, background jobs, web-service consumption, DDIC objects, and more — matched to your actual target SAP system so the first draft compiles and fits, instead of needing several rounds of fixes.

## How to start
Just ask normally, e.g.:
- "Build a RAP BO for sales order approval"
- "Create a CDS view joining VBAK and VBAP with a margin calculation"
- "I need an OData service exposing purchase order approval, S/4HANA Cloud"
- "Fix this AMDP method, it's timing out" (paste the code)

You don't need to name the skill — mentioning ABAP, S/4HANA, CDS, RAP, Clean Core, or BTP ABAP Environment is enough for it to kick in.

## What happens next
1. **A few tappable-button questions** appear in a small widget — things like which environment edition you're on, what scope of change this is, and artifact-specific details. Tap an answer, it moves to the next one automatically. You'll see them labeled "Question 1 of X" so you know how many are left.
2. **A details form** appears next, with text fields and placeholder hints (e.g. namespace prefix, package, requirement description). Fill in what you know — anything left blank gets a clearly-flagged placeholder in the generated code instead of a guess.
3. You get the generated code back, already checked against Clean Core rules for your declared environment, usually with a matching unit test offered alongside.

## Worth having ready before you start
- **Target environment**: On-Premise / Cloud Private Edition / Cloud Public Edition / BTP ABAP Environment — this is asked every time and changes what's even legal to generate, so an accurate answer here saves the most rework.
- **Namespace**: Z or Y prefix, and target package (local `$TMP` or a transportable package + transport request, if you have one).
- If you're **fixing or enhancing** something: the actual existing code, table/CDS structure, or exact error message. Pasting this is the single biggest time-saver — guessed structures are the most common reason for a second round.
- A **custom authorization object** name, if you're checking against one that isn't standard.

Anything you don't have yet — skip it. The flow is designed to keep moving with partial answers.

## A few things to know
- Questions adapt to your environment automatically — e.g. you won't be asked your Basis release on Cloud Public Edition, and illegal options (like Unmanaged RAP, or classic ALV/Dynpro/WebDynpro) just won't appear as choices once you've picked a cloud edition.
- If a whole category of work genuinely isn't legal for your edition (e.g. classic Smart Forms under Cloud Public Edition), you'll get a clear note about that plus the modern alternative — not silently-wrong code.
- "Not sure" is a valid answer on most questions — it just means the skill defaults to the safest, most conservative pattern and says so.

## What this skill won't do
- Non-ABAP BTP services — Integration Suite iFlows/Groovy scripting, CAP (Node/Java), Event Mesh, SAP Build Process Automation. ABAP only.
- Actual role/PFCG user assignment, transport release, or any other Basis/security decision — it'll tell you the steps, but those happen outside ABAP.
