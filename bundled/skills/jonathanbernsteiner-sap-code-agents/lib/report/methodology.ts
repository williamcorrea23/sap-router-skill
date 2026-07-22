/**
 * CO-07/CO-09 — the methodology & data provenance section, shared verbatim by
 * the MD export, the PDF export and the on-screen report (this module stays
 * dependency-free so the client page can import it). Static truthful
 * statements about how the report is produced; the only data-dependent line
 * is usage provenance.
 */

export const SIMPL_LIST_URL =
  "https://help.sap.com/doc/c34b5ef72430484cb4d8895d5edd12af/2023/en-US/SIMPL_OP2023.pdf";

export function methodologyParagraphs(data: {
  has_usage_data: boolean;
  simulated_usage: boolean;
}): { heading: string; text: string }[] {
  const usage = !data.has_usage_data
    ? "This system has no usage statistics, so retirement analysis and usage columns are shown as unavailable rather than estimated."
    : data.simulated_usage
      ? "Usage statistics in this system are SIMULATED (synthetic usage data, deterministic model) and labeled as such everywhere they appear. In a production engagement they come from the system's own execution statistics (SCMON/UPL, ST03N) through the extraction adapter."
      : "Usage statistics come from the system's recorded execution data.";
  return [
    {
      heading: "Evidence tiers",
      text: "Tier 1 findings are machine-verified: a deterministic validator confirmed the incompatibility on the cited line. Tier 2 findings are evidence-linked: the citation was located verbatim in the stored source, but the interpretation needs expert review. Tier 3 items are unverified observations from the current run — transient by design: because their citations could not be located verbatim, they are never counted in headline numbers and are not persisted across runs.",
    },
    {
      heading: "Rules and sources",
      text: `Every incompatibility rule is seeded reference data citing an official SAP Note and its Simplification Item, with a verbatim excerpt from the public Simplification List for SAP S/4HANA 2023 (${SIMPL_LIST_URL}). Note numbers render only for rules whose sources were explicitly verified.`,
    },
    {
      heading: "Risk grades",
      text: "Each object's Migration Risk Grade is computed by SQL from the latest run's findings: D = at least one Tier-1 finding from a severity-high rule (construct removed outright in S/4HANA); C = at least one Tier-1 finding, none severity-high (data model replaced, compatibility views cover transitional reads); B = Tier-2 findings only; A = no Tier-1 or Tier-2 findings. Objects in a system without a finished run are ungraded, never A.",
    },
    {
      heading: "Effort bands",
      text: "Remediation effort (low / medium / high) is a deterministic band seeded per rule — never an estimate produced by a model and never a per-object promise. High means the construct or process must be redesigned; medium means reads keep working via compatibility views but writes or performance need rework; low means mostly mechanical adaptation.",
    },
    {
      heading: "Numbers and stability",
      text: "Every count and percentage is computed by the database, never by a language model; the executive summary's prose is checked against the run's frozen numbers and replaced by a deterministic template if it invents any. Re-runs re-verify each previous Tier-2 finding verbatim against the stored source and carry it forward unchanged, so findings keep stable identities across runs; findings whose evidence no longer matches the source are dropped automatically.",
    },
    { heading: "Usage data", text: usage },
  ];
}
