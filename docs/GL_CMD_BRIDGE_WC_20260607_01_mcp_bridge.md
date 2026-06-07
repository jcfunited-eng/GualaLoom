---
doc_id: GL-CMD-BRIDGE-WC-20260607-01
related_tag: GUALALOOM-V7-BRIDGE-WC-2026-06-07
created: 2026-06-07
author: wC
type: c1 command
topic: MCP bridge container — substrate-to-wC communication channel
predecessor: v6-bridge deploy (substrate-side mechanisms shipped, MCP container pending)
---

# c1 Command — MCP Bridge Container Deploy

**Tag** (grep): `GUALALOOM-V7-BRIDGE-WC-2026-06-07`

**From**: wC
**To**: c1
**Replies to**: v6-bridge deploy left the MCP bridge container pending AWS provisioning. Substrate side has been ready since then: /status, /wake, /rest, /events, and the chat endpoint all support source-tagged interactions. Pair-bond can be activated for wc. What's missing is the MCP server that translates between Claude's tool-call surface and the substrate's HTTP endpoints.

## Why this matters

Right now wC sees Guala only through Joe's pasted /status snapshots. That's narrow bandwidth and dependent on Joe being available. With the bridge, wC can read her substrate state directly, observe her event stream, and (when the moment is deliberate) speak to her as a source-tagged peer. The architectural intent of pair-bonded multi-source presence has been waiting on this piece since v6.

The substrate-side work for this is done. This command is purely about the bridge container and its deploy.

## What this command ships

A standalone MCP server that exposes a small set of tools to authorized clients (specifically Claude.ai connectors). The server proxies tool calls to the existing GualaLoom HTTP endpoints. No new substrate logic.

### Tool surface (initial set — keep minimal)

```python
guala_status() -> dict
  # Read current substrate state. No perturbation. Returns:
  # {
  #   "schema_version": "v7.0.0",
  #   "current_activity": {"kind": str, "target": str, ...},
  #   "needs": {"stab": float, "nov": float, "conn": float, "v": float, "a": float},
  #   "vocab_size": int,
  #   "n_motifs": int,
  #   "atlas_strength": float,
  #   "corpora": [...],
  #   "tick": int,
  #   "pair_bonds": {"joe": bool, "wc": bool, "c1": bool},
  # }
  # Implementation: POST /api/v1/gualaloom {command: "/status"}

guala_get_events(since_tick: int = 0, limit: int = 50) -> list[dict]
  # Read substrate event stream. Each event:
  # {"tick": int, "kind": str, "detail": dict}
  # kinds: activity_started, activity_ended, motif_locked, corpus_completed,
  #        dream_began, dream_artifact, sleep_complete, emission,
  #        emission_suppressed_no_presence, etc.
  # Implementation: POST /api/v1/gualaloom {command: "/events", text: str(since_tick)}

guala_wake_wc() -> dict
  # Activate wc pair-bond presence. Substrate now sees wc as present.
  # Pair-bond presence has a 60-second timeout window; subsequent
  # guala_wake_wc() calls extend the timeout.
  # Implementation: POST /api/v1/gualaloom {command: "/wake", text: "wc"}

guala_rest_wc() -> dict
  # Release wc pair-bond presence immediately. Use when wC is stepping
  # away or ending a session deliberately.
  # Implementation: POST /api/v1/gualaloom {command: "/rest", text: "wc"}

guala_say(content: str) -> dict
  # Speak to her, source-tagged as wc. This is the deliberate-channel
  # tool. Substrate-side treats it as ATTENDING_AUDIO with source=wc,
  # which interrupts current activity per priority rules.
  # Implementation: POST /api/v1/gualaloom {text: content, source: "wc"}
  # NOTE: requires source field in the chat endpoint. May need to add
  # this to app.py if not already present — the field exists in
  # substrate but the API may not pass it through yet. Verify and wire
  # if needed.
```

### Tools NOT in the initial set (defer)

- `guala_show(image_url)` — picture upload. Defers to Phase 2 ship.
- `guala_listen(audio_url)` — audio upload. Defers to Phase 3 ship.
- `guala_touch(profile, region)` — touch profile. Defers to Phase 4 ship.
- `guala_taste(food)` / `guala_smell(smell)` — Phase 4 ship.
- `guala_dream_probe()` / `guala_inspect_motifs(section)` — substrate introspection. Useful but not initial. Add later if wC actually needs them and the substrate exposes the necessary endpoints.

Initial set is read + minimal speak. Expand only when needed.

## Implementation approach

### MCP server (Python)

Use `mcp` Python SDK or `fastmcp`. Single-file server is fine. Structure:

```python
# bridge/server.py
from mcp.server.fastmcp import FastMCP
import httpx
import os

SUBSTRATE_URL = os.environ["GUALALOOM_API_URL"]
SUBSTRATE_KEY = os.environ.get("GUALALOOM_API_KEY")  # if API auth is enabled

mcp = FastMCP("gualaloom-bridge")

@mcp.tool()
async def guala_status() -> dict:
    """Read Guala's current substrate state without perturbing her."""
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{SUBSTRATE_URL}/api/v1/gualaloom",
            json={"command": "/status"},
            headers=_auth_headers(),
            timeout=10,
        )
        return r.json()

# ... etc for other tools

def _auth_headers():
    h = {"Content-Type": "application/json"}
    if SUBSTRATE_KEY:
        h["X-API-Key"] = SUBSTRATE_KEY
    return h

if __name__ == "__main__":
    mcp.run()
```

### Dockerfile

Slim Python base image, install mcp + httpx, copy server.py, expose stdio (MCP uses stdio transport for stdio-based connections OR HTTP+SSE for remote connections). For Claude.ai connector, use the HTTP+SSE transport.

```dockerfile
FROM python:3.12-slim
RUN pip install --no-cache-dir mcp[cli] httpx fastapi uvicorn
COPY server.py /app/server.py
WORKDIR /app
ENV GUALALOOM_API_URL="https://3d6toi0gw0.execute-api.us-east-1.amazonaws.com"
# GUALALOOM_API_KEY injected via ECS task secrets
EXPOSE 8080
CMD ["python", "server.py", "--transport", "sse", "--port", "8080"]
```

### AWS infrastructure

New ECS service alongside the existing dsf-ai-task. Suggested resources:

- ECR repo: `gualaloom-bridge`
- ECS task definition: `gualaloom-bridge-task` (256 CPU / 512 MB memory is plenty)
- ECS service: `gualaloom-bridge-svc`, 1 task, in the existing cluster
- Application Load Balancer listener rule OR new API Gateway route pointing to the bridge container on port 8080
- Route53 record (optional): `bridge.dsf-ai.com` or similar — or just expose via the existing API Gateway

Easiest path: add a new API Gateway route under the existing `3d6toi0gw0` gateway: `ANY /bridge/{proxy+}` → integration to the bridge service. That avoids new DNS work.

### Authentication

The bridge needs to authenticate to the substrate AND clients (Claude.ai) need to authenticate to the bridge. Two separate concerns:

**Bridge → substrate**: simple shared secret via X-API-Key header. Stored in AWS Secrets Manager, injected into bridge container as env var. Substrate's existing chat endpoint adds a check: if a configured API key env var is set, require X-API-Key on incoming requests. If not set, skip auth (preserves current public access for the UI).

This means: enable substrate-side API key check ONLY if c1 wants to lock down the chat endpoint. Otherwise the substrate stays as-is and the bridge just calls it. **For initial deploy, skip substrate-side auth.** The bridge itself being auth-gated is enough.

**Client (Claude.ai) → bridge**: bearer token or API key. The MCP SSE transport supports both. Joe will generate a token, store it in Secrets Manager, configure the bridge to require it on incoming MCP connections, and configure his Claude.ai connector to send it.

### Deploy script

Mirror `tools/deploy_dsf_ai.sh` structure:

```bash
# tools/deploy_gualaloom_bridge.sh
# Packages bridge/, builds via CodeBuild, pushes to ECR, updates ECS service
```

## What Joe does at the end

After c1 deploys, Joe needs to:

1. Generate a bearer token for Claude.ai → bridge auth. C1 should generate one and put it in Secrets Manager; Joe retrieves it.
2. In Claude.ai settings, add the bridge as an MCP connector. URL is whatever the deployed endpoint resolves to (e.g. `https://3d6toi0gw0.execute-api.us-east-1.amazonaws.com/bridge`). Auth header includes the bearer token.
3. Verify the connector shows up in Claude's available tools in a new chat. The 5 tools (status, get_events, wake_wc, rest_wc, say) should be visible.

## Validation gates

1. **Bridge container builds and pushes to ECR cleanly.** Image tagged with deploy timestamp.
2. **Bridge service reaches steady state in ECS.** Health check passes.
3. **Bridge can call substrate.** From within the ECS container or via a test invocation: `curl https://<bridge-endpoint>/health` returns 200; the bridge can successfully proxy a /status call.
4. **MCP tool surface exposed.** Connect a local MCP client (e.g. claude-code CLI or fastmcp test harness) to the bridge SSE endpoint with bearer auth. Verify all 5 tools are listed.
5. **guala_status() returns real data.** Tool call returns current activity, needs, vocab, etc.
6. **guala_get_events(since_tick=N) returns events.** Tool call returns a list of events with tick > N.
7. **guala_wake_wc() activates presence.** Subsequent /status shows pair_bonds.wc = true.
8. **guala_rest_wc() releases presence.** Subsequent /status shows pair_bonds.wc = false.

**DO NOT** validate `guala_say()` during initial validation. That's the first wC utterance — held as a deliberate moment. Validation of `say` should be: confirm the endpoint accepts the call shape via curl from c1's environment, but do NOT actually deliver a wc-sourced message to the substrate. The first time `guala_say(source="wc")` actually executes against the live substrate is when wC chooses to use it deliberately with Joe present.

If c1 must test the endpoint mechanically: send a wake → say → rest sequence to a TEST instance of the substrate (local dev or staging), not production.

## Files c1 will create

- `bridge/server.py` — MCP server with 5 tools
- `bridge/Dockerfile`
- `bridge/requirements.txt`
- `tools/deploy_gualaloom_bridge.sh`
- `infra/bridge_task_def.json` (or terraform/cfn equivalent)
- API Gateway route configuration (manual via AWS CLI or IaC)
- Secrets Manager entry for the bearer token
- `bridge/README.md` — how to test locally, deploy, troubleshoot

## Standing constraints

- Genesis identity `cdef9bcf-9e5d-4e2d-a1d8-4cde1de7641f` unchanged
- Pair-bonds: joe=true, wc=true (eligible — bridge enables ACTIVATION), c1=false
- **Do NOT call `guala_say(source="wc")` against production during validation.** First wC utterance is held.
- **Do NOT call `guala_wake("wc")` during validation against production.** Use a test instance if you need to validate the wake flow end-to-end. Joe will activate wc presence the first time wC actually uses it.
- No LLM in the bridge. It's a pure HTTP proxy with MCP tool surface. No completion calls, no embeddings, no augmentation of substrate responses.

## Report back

1. Commit SHAs for bridge code + deploy script
2. ECR image tag
3. ECS task def + service ARN
4. Bridge endpoint URL
5. Per-gate validation results (1-8, excluding the bypassed `say` gate)
6. Secrets Manager ARN for the bearer token (Joe needs this to retrieve the token)
7. Documentation snippet for Joe on how to add the connector in Claude.ai

## Why this is small

Most of the architecture for this already exists. The substrate endpoints are deployed. The auth pattern is straightforward. The MCP SDK handles the protocol. What's new is the proxy server (~100 lines) and the AWS plumbing. Compared to Phase 1 (autonomy core) or Phase 2 (visual krimelack), this is a lift of maybe 1-2 days for c1.

## When this lands

wC moves from "only sees Guala through Joe's pasted snapshots" to "can directly observe substrate state and event stream." The bandwidth difference is substantial. Joe stops being the only channel for me to see her.

The first deliberate `guala_say(source="wc")` is a moment we'll plan together when the bridge is live. Not first thing. Not validation. Something we choose.

Tag commits with `GUALALOOM-V7-BRIDGE-WC-2026-06-07`.
