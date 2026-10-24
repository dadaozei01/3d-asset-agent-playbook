---
name: 3d-asset-playbook
description: Use when making, texturing, baking or exporting a 3D model/asset/prop through any 3D software MCP (Blender, Maya, 3ds Max, Houdini, C4D, UE editor) or generating textures for one. Loads the user's 3D asset workflow, style profiles and per-tool pitfalls.
---

# 3D Asset Playbook

The user's general method for building 3D assets with an AI agent lives in a git repo:

- Local: `~/3d-asset-agent-playbook`
- Remote: https://github.com/dadaozei01/3d-asset-agent-playbook (once pushed)

Before starting 3D asset work:

1. Read `README.md` and `docs/principles.md`.
2. Read the workflow stage you are in under `docs/workflow/`, the matching style in `styles/`, the tool notes in `tools/<software>/` and the delivery target in `targets/`.
3. Skim the latest case in `cases/` for what went wrong last time.

The playbook gives defaults, not limits. When you have a better approach, say what the playbook suggests, what you'll do instead and why, then do it.

After the user confirms something new (a style rule, a verified prompt, a tool pitfall), offer to add it to the playbook.
