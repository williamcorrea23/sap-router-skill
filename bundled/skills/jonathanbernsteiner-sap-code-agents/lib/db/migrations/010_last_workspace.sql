-- IA refinement: the app root routes to the user's last-used workspace.
-- Persisted per user (not per browser); deleting the workspace clears it
-- automatically, so the root falls back to Connections.
alter table profiles
  add column last_workspace_id uuid references workspaces(id) on delete set null;
