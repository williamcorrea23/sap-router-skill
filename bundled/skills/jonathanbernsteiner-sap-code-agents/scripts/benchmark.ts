/**
 * Phase 4 benchmark runner: executes every question in benchmark/questions.json
 * through the REAL agent loop (lib/agent/loop.ts — live Anthropic API + live
 * database) and machine-checks expected_behavior.
 *
 *   npx tsx --env-file=.env.local scripts/benchmark.ts        # all questions
 *   npx tsx --env-file=.env.local scripts/benchmark.ts b3     # id prefix filter
 *
 * Exit code 0 only if every question passes.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { closePool } from "../lib/db/client";
import { runAgent, type AgentEvent } from "../lib/agent/loop";

interface Question {
  id: string;
  workspace: string;
  question: string;
  expected_behavior: {
    must_use_tools: string[];
    answer_matches: string[];
    answer_not_matches: string[];
  };
}

async function runOne(q: Question): Promise<{ pass: boolean; problems: string[]; toolCalls: string[] }> {
  const toolCalls: string[] = [];
  const events: AgentEvent[] = [];
  const answer = await runAgent({
    workspaceName: q.workspace,
    turns: [{ role: "user", content: q.question }],
    onEvent: (e) => {
      events.push(e);
      if (e.type === "tool_use") toolCalls.push(e.name);
    },
  });

  const problems: string[] = [];
  if (events.some((e) => e.type === "error")) {
    problems.push(`agent error: ${(events.find((e) => e.type === "error") as { message: string }).message}`);
  }
  for (const tool of q.expected_behavior.must_use_tools) {
    if (!toolCalls.includes(tool)) problems.push(`expected tool '${tool}' was not called (called: ${toolCalls.join(", ") || "none"})`);
  }
  for (const pattern of q.expected_behavior.answer_matches) {
    if (!new RegExp(pattern, "i").test(answer)) problems.push(`answer does not match /${pattern}/i`);
  }
  for (const pattern of q.expected_behavior.answer_not_matches) {
    if (new RegExp(pattern, "i").test(answer)) problems.push(`answer must NOT match /${pattern}/i but does`);
  }
  if (toolCalls.length === 0) problems.push("agent used no tools at all");
  if (toolCalls.length > 10) problems.push(`agent used ${toolCalls.length} tool calls (max 10)`);
  return { pass: problems.length === 0, problems, toolCalls };
}

async function main() {
  const filter = process.argv[2];
  const { questions } = JSON.parse(
    readFileSync(join(import.meta.dirname, "..", "benchmark", "questions.json"), "utf8")
  ) as { questions: Question[] };
  const selected = filter ? questions.filter((q) => q.id.startsWith(filter)) : questions;

  let failed = 0;
  for (const q of selected) {
    process.stdout.write(`[${q.id}] (${q.workspace}) ${q.question.slice(0, 70)} ... `);
    try {
      const r = await runOne(q);
      if (r.pass) {
        console.log(`PASS (${r.toolCalls.length} tool calls: ${r.toolCalls.join(", ")})`);
      } else {
        failed++;
        console.log("FAIL");
        for (const p of r.problems) console.log(`    - ${p}`);
      }
    } catch (e) {
      failed++;
      console.log(`FAIL (exception: ${(e as Error).message})`);
    }
  }
  console.log(`\n${selected.length - failed}/${selected.length} passed`);
  await closePool();
  process.exit(failed === 0 ? 0 : 1);
}

main();
