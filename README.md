# Proposal & Scope-of-Work Drafting Assistant

A simple local application using **FastAPI, scikit-learn, HTML, CSS and JavaScript**. Paste discovery notes, select a service package and template, generate a draft, review missing information, edit the understanding/objectives or add reviewer amendments, and download a Word document.

## Run on Windows (Python 3.12 recommended)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000. API documentation is at `/docs`. No API key, database or environment variables are required. Keep the server bound to localhost; this single-user prototype has no authentication and is not intended for public hosting.

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## How it works

`app/model.py` trains a TF-IDF + LogisticRegression pipeline at startup using 36 clearly illustrative labelled examples. It assigns discovery statements to objective, deliverable, dependency, timeline, question or context categories. This is a real, small supervised classifier, not a generative language model. Categories are suggestions; no production accuracy is claimed. The example corpus is too small for reliable business use without evaluation on representative labelled notes.

`app/drafting.py` deterministically assembles typed drafts from `data/catalogue.json`. Discovery objectives and evidence retain their original wording and are explicitly unconfirmed. Package scope is never expanded by the classifier. Every package milestone has an unconfirmed date. Inputs for requested timeline and approver are retained as supplied, not treated as contractual commitments. Missing fields and possible scope conflicts become visible questions.

`app/main.py` serves the frontend and three API endpoints: catalogue, draft, and DOCX export. Export regenerates the protected content from the selected server-side records, then adds reviewer edits. `app/schemas.py` validates requests and the draft output. No notes or drafts are stored on disk or sent to external services. Refreshing loses the draft. No automatic sending, signatures, accounts, history or other services are included.

## Company configuration and safeguards

No real company documents were supplied. Basic, Standard, Premium, Custom and Consultation package options are **professional package options with recommended scope, deliverables and planning ranges**; the existing Data analysis and ML prototype samples remain available. The seven requested proposal templates are selectable but **unapproved draft formats**; the neutral draft option also remains. Replace/configure these with authorized company records in `data/catalogue.json` before business use. The local file is trusted administrator configuration; the API cannot edit it.

- Package fields: `id`, `name`, `version`, `sample`, `scope`, `deliverables`, `assumptions`, `exclusions`, `exclusion_keywords`, `dependencies`, `milestones`, `pricing`.
- Pricing defaults to `null`. To use supplied pricing, set `pricing` to an object with `approved: true`, `source: "actual approval reference"`, and `text: "exact approved commercial wording"`. Preserve currency and units in that text. The application does not estimate prices or compute totals. Approval metadata must be set only by an authorized person.
- Templates have `id`, `name`, `version`, `approved`, `fixed_wording` and `section_order`. Use all existing section keys in `section_order`. Insert actual approved fixed wording verbatim and set approval metadata only when supported. Template layout is a supported JSON section layout, not an arbitrary uploaded Word template.
- Fixed wording and package content are read-only in the preview and regenerated during export. Understanding and objectives are editable; export labels changed text as unconfirmed reviewer amendments. Commercial edits are blocked with a conservative keyword filter; authorized pricing belongs in package configuration.
- Pricing-like discovery statements are withheld from the draft and marked unverified. There is no language-model instruction execution. Notes cannot override the package, template or pricing fields. Untrusted text is inserted into the browser with `textContent` or textarea values, never HTML.
- The output always remains a draft, with outstanding questions, source/version references and a neutral-template warning where appropriate. External sharing is manual.

## Limitations

The classifier uses a small English demonstration corpus. It can misclassify statements; it does not verify client claims. Scope conflict checks use configured keywords, may flag negated statements, and cannot detect every semantic conflict. Commercial keyword filtering is conservative, not a complete language understanding system. Human reviewers must verify any manually entered text and all commitments. Draft statements, reviewer edits and requested timelines do not become approved scope. There is no arbitrary template upload or exact Word template fidelity. DOCX export uses simple headings and bullets; PDF is not included.

Critical tests cover missing information, price source rules, injection resistance, conflicts, immutable template wording, invalid inputs, protected export fields, and opening the resulting DOCX. Before real business use, replace sample content with approved company records and evaluate the classifier on representative examples.

## Delivery validation

On 28 October 2026: `python -m pytest -q` passed all 15 tests, and `node --check static/app.js` passed. A live browser check confirmed sample-note submission, the generated preview, missing-pricing warning and scope conflict. DOCX files were reopened programmatically; visual verification in Microsoft Word was not performed. The installed Starlette test client emits a non-failing deprecation warning about its HTTPX integration.

Package guidance: Basic 1-2 weeks, Standard 3-6 weeks, Premium 6-10 weeks, Consultation 3-5 working days; Custom is scoped individually. These are configurable planning recommendations authorized for this prototype, not estimates validated against client requirements or approved commitments. Pricing is never inferred. The brief guidance recommends 40-150 words while retaining the 10-character minimum.
