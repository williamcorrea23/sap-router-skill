-- Source provenance: the branch a repo-ingested workspace was cloned from,
-- recorded at ingestion time. Used to deep-link file:line citations to the
-- repo host (blob/<branch>/<path>#L<line>); null for fixture workspaces and
-- pre-existing ingestions (links then fall back to HEAD).
alter table workspaces add column source_branch text;
