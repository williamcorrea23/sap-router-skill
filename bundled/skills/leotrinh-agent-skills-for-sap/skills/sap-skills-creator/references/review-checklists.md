# Review Checklists

Load this file at the end of each phase to confirm completion, and again
at the very end of the workflow.

Each checklist is intentionally short. It complements, not replaces, the
full guidance in the other reference files.

## Creator Checklist

Use during the Create and Refactor modes.

- [ ] Verified source of expertise exists.
- [ ] Scope statement passes the coherent-unit test.
- [ ] Requirements template is filled in.
- [ ] Frontmatter is valid, matches the directory, and stays inside
      length limits.
- [ ] `SKILL.md` follows the workflow phases and stays within 300–450
      lines (hard limit 500).
- [ ] Reference files are focused, linked from `SKILL.md`, and free of
      nested reference mazes.
- [ ] Templates in `assets/` use placeholders only.
- [ ] Scripts, if any, follow the script rules in
      [`scripts-and-resources.md`](scripts-and-resources.md).
- [ ] Structural validation returns no `FAIL`.
- [ ] Behavioural evaluation ran at least one execute-review-revise
      cycle.
- [ ] Output contract is documented.
- [ ] Completion checklist inside `SKILL.md` matches the actual behaviour
      of the skill.

## Reviewer Checklist

Use during the Audit mode, and during code review of any submitted
skill.

- [ ] The description clearly states what the skill does and when to use
      it.
- [ ] Positive and negative triggers exist and are meaningful.
- [ ] The workflow is procedural, not declarative.
- [ ] Every claim about SAP behaviour has a traceable source.
- [ ] The skill does not invent SAP endpoints, authorization objects, or
      product features.
- [ ] Risk classification is present and matches the operations the skill
      exposes.
- [ ] Required credentials are resolved outside the AI conversation.
- [ ] Destructive operations require explicit human authorization at the
      moment of execution.
- [ ] Scripts follow the shared script rules.
- [ ] Structural validator was executed and its findings are recorded.
- [ ] Behavioural evaluation results are recorded.

## Security Checklist

Use during the Security Review phase.

- [ ] No hardcoded passwords, tokens, cookies, private keys, or
      certificates.
- [ ] No real destination credentials, hostnames, or SIDs.
- [ ] No `.env` files with values.
- [ ] TLS verification enabled by default. Insecure mode requires an
      explicit flag and warns on stderr.
- [ ] Every network operation has a timeout.
- [ ] Every subprocess call uses argument arrays or explicit quoting.
- [ ] No secrets appear in stdout, stderr, exception messages, or logs.
- [ ] Destructive operations follow the
      inspect–confirm–preview–authorize–execute–verify–report sequence.
- [ ] Every dependency is pinned and justified.
- [ ] No prebuilt executable is committed to the default branch.
- [ ] Public releases include a non-affiliation disclaimer with SAP SE.

## Public-Release Checklist

Use before recommending the skill for public release.

- [ ] License compatibility confirmed for every included file, including
      images.
- [ ] Trademark disclaimer present and correct.
- [ ] Full security scan re-run against the final state.
- [ ] Customer-identifiable material removed.
- [ ] Proprietary code removed or replaced with sanitised examples.
- [ ] Human-readable `README.md` present, current, and complete.
- [ ] Security-reporting instructions present.
- [ ] Repository is public and its metadata is current.

## SAP AI Skills Library Checklist

Use before drafting the registration issue.

- [ ] Repository is public.
- [ ] Each skill under `skills/<slug>/SKILL.md` passes the readiness
      checklist.
- [ ] Skill discovery works against the public URL.
- [ ] License information is available.
- [ ] Author information is available.
- [ ] Description is trigger-rich and stays within the length limit.
- [ ] Additional context template is filled in and reviewed.
- [ ] No claim of SAP approval, certification, or endorsement appears in
      any material.
- [ ] The maintainer, not the agent, submits the registration issue.

## Refactor Checklist

Use during the Refactor mode.

- [ ] Behavioural intent of the existing skill is preserved.
- [ ] Existing useful knowledge is preserved.
- [ ] Existing command compatibility is preserved.
- [ ] Content moved between files is recorded in the change report.
- [ ] Content removed is recorded with a reason.
- [ ] Security posture is documented, including any changes.
- [ ] Trigger behaviour is documented before and after the refactor.
- [ ] Compatibility risks are flagged for review.
- [ ] Structural validator returns no new `FAIL`.
- [ ] Behavioural evaluation confirms no regression in trigger precision
      or safety behaviour.
