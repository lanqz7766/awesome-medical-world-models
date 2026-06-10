# Contributing

Thanks for helping keep this list accurate and useful!

## How to add or fix an entry

1. Edit [`data/medical_world_models.csv`](data/medical_world_models.csv) — one row per paper.
2. Run `python generate_readme.py` to regenerate `README.md` from the CSV.
3. Open a pull request with both the CSV change and the regenerated `README.md`.

Please do **not** hand-edit `README.md` directly; it is generated.

## Column guide

| Column | Notes |
|---|---|
| `paper_id` | Stable id (e.g. `MWM0162`); use the next free number for new entries. |
| `title`, `authors`, `year`, `venue` | `authors` is `First Last; First2 Last2; …`. |
| `url`, `doi`, `arxiv_id`, `pdf_url` | A resolvable `url` is required. |
| `code_url` | Public repo if one exists. |
| `code_available` | `yes` only if you can link/confirm a public repo; otherwise `unknown`. |
| `capability_level` | One of `L0`/`L1`/`L2`/`L3`/`L4` (+ free text). Use `L1` for L1b continuous-time models and note it in the description. |
| `topic_track` | One of the seven `T1`–`T7` track ids (see README sections). |
| `inclusion_tier` | `core` (self-identifies as a medical world model), `near_core`, or `background`. |
| `state_representation`, `action_or_intervention`, `transition_model`, `outcome_or_reward`, `validation_level` | The SATO-V fields. |
| `description` | One sentence, plain text. |

## The conservative public-evidence rule

This list codes from **public artifacts only**. If code availability, dataset access, or a validation protocol is not clearly evidenced in the paper, its repository, or official metadata, mark the field **`unknown` / `not_reported`** rather than asserting absence. A missing field means "not publicly evidenced," not "does not exist." This keeps the list honest about an emerging field.

## Scope

In scope: models and systems (and closely related reviews, position papers, digital-twin systems, and foundational methods) relevant to **medical / clinical world modeling** — representing patient or environment state, simulating transitions, conditioning on clinical actions, or planning. Out of scope: general-domain world models with no medical application, and pure static-diagnosis papers with no temporal/simulation/planning component.
