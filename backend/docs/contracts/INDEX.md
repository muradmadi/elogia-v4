# API Contracts — Elogia v4 Backend

> Auto-discovered service web contracts for the Elogia v4 backend. These documents explain every backend interface from each service's first-person perspective, written for frontend developers.

## Discovered Service Webs

| Web Name | Services | Contract |
|----------|----------|----------|
| Enrichment Pipeline | ClayWebhookService, EnrichmentService | [enrichment_pipeline.md](./enrichment_pipeline.md) |
| Sequence Generation Pipeline | SequenceService, GenerationService, LLMService | [sequence_generation_pipeline.md](./sequence_generation_pipeline.md) |
| Content Pipeline | AssetService, N8nService | [content_pipeline.md](./content_pipeline.md) |

## Quick Reference

### Enrichment Pipeline
**What it does:** Sends an email to Clay for enrichment, receives 6 webhook callbacks with structured data, stores them as JSONB payloads, and transforms raw payloads into a clean `LeadProfileView` for downstream consumption.

**Key endpoints:**
- `POST /webhooks/trigger` — Start enrichment for an email
- `POST /webhooks/clay` — Receive Clay webhook callbacks
- `GET /api/enrichment/completed` — List completed enrichment jobs
- `GET /api/enrichment/{job_id}/payload` — Get raw JSONB payloads
- `GET /api/enrichment/{job_id}/profile` — Get transformed lead profile
- `GET /api/enrichment/jobs/{job_id}` — Get job by ID
- `PUT /api/enrichment/jobs/{job_id}` — Update job
- `DELETE /api/enrichment/jobs/{job_id}` — Delete job

**Entities:** EnrichmentJob

**Downstream:** Feeds `LeadProfileView` into the Sequence Generation Pipeline

---

### Sequence Generation Pipeline
**What it does:** Picks a completed enrichment, transforms it into a structured lead profile, sends it to Claude LLM for hyper-personalized 8-touch email sequence generation, validates the response, and serves the structured sequence to the frontend.

**Key endpoints:**
- `POST /api/sequence/generate/{job_id}` — Trigger sequence generation
- `GET /api/sequence/job/{job_id}` — Get generated sequence data

**Entities:** CampaignSequence

**Upstream:** Consumes `LeadProfileView` from the Enrichment Pipeline

---

### Content Pipeline
**What it does:** Uploads PDF marketing assets, triggers n8n content shredder for automated content extraction, receives LinkedIn posts and email pills via callback, and serves structured content to the frontend.

**Key endpoints:**
- `POST /api/assets/upload` — Upload PDF asset
- `POST /api/assets/webhook/n8n-callback` — Receive n8n callback
- `GET /api/assets/{asset_id}/snacks` — Get asset with content snacks
- `GET /api/assets/{asset_id}/content` — Get cleaned content for an asset

**Entities:** MarketingAsset, ContentSnack

---

### Health Check (Standalone)
**What it does:** Basic API health and readiness monitoring.

**Key endpoints:**
- `GET /health/status` — Basic health check
- `GET /health/ready` — Readiness check with database connectivity
- `GET /health/live` — Liveness check for Kubernetes/Docker probes

---

## Discovery Summary

- **Total services:** 7 (ClayWebhookService, EnrichmentService, GenerationService, LLMService, SequenceService, AssetService, N8nService)
- **Total webs:** 3
- **Total HTTP endpoints:** 17 (14 across 3 webs + 3 health check)
- **Last generated:** 2026-03-21
- **Orphaned services:** None

## How to Use These Contracts

1. **Find the web** you're working with in the table above
2. **Open the contract file** and navigate to the relevant section:
   - **Section 4 (External API Contracts)** — HTTP endpoints you'll call from the frontend
   - **Section 5 (Data Flow)** — How data transforms as it moves through the pipeline
   - **Section 6 (Status State Machine)** — Entity status transitions and polling strategies
   - **Section 7 (Error Contracts)** — What errors to expect and how to handle them
3. **Check the Pydantic schema tables** inline in each section for exact field names, types, and descriptions
4. **Use the Mermaid diagrams** to understand the request/response flow visually
