# Enrichment Payload Endpoints Contract

This document defines the API contract for individual payload endpoints for an enrichment job.

## Base URL
`/api/enrichment/{job_id}`

## Endpoints

| Endpoint | Method | Response Schema | Description |
| :--- | :--- | :--- | :--- |
| `/person` | GET | `PersonSchema` | Returns transformed person data |
| `/company` | GET | `CompanySchema` | Returns transformed company data |
| `/profile` | GET | `ProfileSchema` | Returns transformed profile data |
| `/products` | GET | `ProductSchema[]` | Returns list of transformed product data |
| `/painpoints` | GET | `PainPointsSchema` | Returns transformed pain points data |
| `/communication` | GET | `CommunicationSchema` | Returns transformed communication data |

## Error Handling
- `404 Not Found`: Payload not yet available.
- `500 Internal Server Error`: Transformation error or database error.
