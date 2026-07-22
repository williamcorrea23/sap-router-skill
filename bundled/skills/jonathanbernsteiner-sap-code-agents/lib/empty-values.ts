/**
 * How the product renders a value it does not have. Three cases, three
 * tokens — never mixed, because the difference is load-bearing for a report
 * whose whole claim is that it states what it knows:
 *
 *   NOT_AVAILABLE ("n/a")  the number could NOT be computed, because an input
 *                          is missing (no usage statistics → no retirement
 *                          analysis). Distinct from a real zero: "0
 *                          retirement candidates" means we looked and found
 *                          none; "n/a" means we could not look. Always
 *                          accompanied by the reason.
 *   "0"                    a genuine measured zero.
 *   NO_VALUE ("—")         this row has no such value by nature (a table has
 *                          no execution count), rather than a missing input.
 *
 * "None" is deliberately not used for missing inputs: next to a coverage or
 * usage label it reads as a measured zero — "nothing runs" — which is the
 * opposite of "we have no measurements".
 */
export const NOT_AVAILABLE = "n/a";
export const NO_VALUE = "—";
