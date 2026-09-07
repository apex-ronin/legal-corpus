# legal-corpus (public sample)

Public sample of the Apex Ronin regulatory clause corpus that powers
[`primordial-galaxy`](https://github.com/apex-ronin/primordial-galaxy)'s
antibody agent and `ronin`'s Prism legal-retrieval agent.

**This is a fixed, real 20-clause slice across all 8 domains — not synthetic
data, and not meant to grow.** It exists so the full retrieval pipeline can
be built and run end to end as a working demo. The full 104-clause corpus
is Apex Ronin's private commercial layer.

## Schema

Every file in `corpus/` is a JSON array of clause objects:

| Field         | Type   | Description |
|---------------|--------|-------------|
| `id`          | string | Canonical clause identifier, e.g. `"DFARS 252.204-7021"`. Unique across the corpus. |
| `title`       | string | Official clause title. |
| `vector`      | string | Comma-separated retrieval keywords. |
| `clause_text` | string | Plain-English operative summary of the clause's requirements. |

## Files (20 real clauses, sampled across 8 domains)

| File | Domain | Sample size |
|------|--------|------|
| `far_clauses.json` | Core FAR + OMB policy (M-26-04 / EO 14319) | 4 |
| `cmmc_cyber_clauses.json` | CMMC / DFARS cybersecurity | 3 |
| `data_rights_clauses.json` | Data rights / IP | 3 |
| `competition_clauses.json` | Competition requirements | 2 |
| `gsar_clauses.json` | GSAR | 2 |
| `it_cloud_508_clauses.json` | IT / cloud / Section 508 | 2 |
| `small_business_clauses.json` | Small business set-asides | 2 |
| `state_clauses.json` | State (CA) | 2 |

## Scripts

- `scripts/validate_corpus.py` — schema + uniqueness validation.
- `scripts/build_index.py` — builds a local FAISS index from these clauses.

## Provenance

Clauses drafted against primary sources (acquisition.gov, whitehouse.gov
OMB memos). FAR 52.204-21 / DFARS 252.204-7020 carry a verified
dual-numbering note (2026-09-06) — see the `clause_text` fields.

## License

[PolyForm Shield 1.0.0](LICENSE) — free to use, may not be used to build a
competing product.
