# PRD — PillCheck: Camera-Based Medication Adherence Verifier


| Field           | Value                                          |
| --------------- | ---------------------------------------------- |
| Document status | Draft v1.0                                     |
| Author          | Tirth Shah                                     |
| Last updated    | 2026-07-22                                     |
| Project type    | Portfolio / end-to-end CV system (open-source) |
| Target release  | Phased (see §14)                               |


---

## 1. Problem Statement

Roughly half of patients on chronic medication do not take their medicines as prescribed. The highest-risk group — elderly patients on 5+ concurrent prescriptions (polypharmacy) — routinely confuses visually similar pills, takes the wrong dose, or takes the right pill at the wrong time. Medication errors drive preventable hospitalizations and cost payers ~$100B+ annually in the US alone.

Existing consumer tools (Medisafe and similar) are **reminder-based**: they trust the user's self-report ("I took it"). Clinical-grade verification tools (AiCure) confirm ingestion via video but are pharma-trial-focused, cumbersome, and not available to consumers. **No open, consumer-grade tool visually verifies that the pill in the user's hand is the pill scheduled for that dose.**

PillCheck closes that gap: point a phone camera at the pill(s) in hand; the system identifies each pill (shape + color + size + imprint), checks it against the user's medication schedule, and returns **MATCH / MISMATCH / CANNOT IDENTIFY** — with all image processing on-device for privacy.

**Why this is a strong portfolio project** (per the "good CV project" criteria):

- **Technical depth**: fine-grained low-shot recognition, multi-pill detection, small-text OCR, multimodal fusion, calibrated abstention, on-device optimization.
- **Real-world applicability**: validated market (AiCure, Medisafe), quantifiable pain, benchmark to report against (ePillID).
- **End-to-end**: data pipeline → model training → evaluation → deployed app with UI → documentation.

---



## 2. Goals


| #   | Goal                                                           | Type          | Measure                                                                                                          |
| --- | -------------------------------------------------------------- | ------------- | ---------------------------------------------------------------------------------------------------------------- |
| G1  | Correctly verify a scheduled single pill from a consumer photo | User          | ≥ 95% top-1 verification accuracy on held-out consumer test set; ≥ benchmark parity on ePillID holdout           |
| G2  | Never confidently mis-verify                                   | User / Safety | Wrong-pill-confirmed-as-match rate < 0.5% at operating threshold (abstain instead)                               |
| G3  | Work in real household conditions                              | User          | ≥ 85% task completion (verified or safely abstained with actionable guidance) across varied lighting/backgrounds |
| G4  | Preserve privacy                                               | User          | 100% of image inference on-device; zero pill images leave the device in default mode                             |
| G5  | Demonstrate end-to-end ML engineering                          | Portfolio     | Public repo with reproducible training, eval report vs. ePillID baseline, deployed demo app, decision log        |


---



## 3. Non-Goals (v1)


| Non-goal                                                      | Rationale                                                                                                                                       |
| ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Ingestion confirmation (watching the user swallow)            | AiCure's territory; requires face video, raises privacy burden dramatically; verification-in-hand solves the core mix-up problem                |
| Liquid, inhaled, injected, or topical medications             | Different sensing problem entirely; pills/capsules cover the dominant polypharmacy risk                                                         |
| Drug–drug interaction checking                                | Requires clinical knowledge base and regulatory care; separate initiative — schedule data model must not preclude it (P2)                       |
| Prescription intake via pharmacy/EHR integration (e.g., FHIR) | High integration cost; v1 uses manual + photo-assisted schedule setup. Data model designed to accept NDC codes so integration can bolt on later |
| FDA/medical-device certification                              | v1 is an assistive consumer/portfolio tool with explicit disclaimers; certification is a company-scale effort                                   |
| Counterfeit-drug detection                                    | Requires microscopic/spectral features beyond phone cameras                                                                                     |


---



## 4. User Personas


| Persona                                            | Description                                                                                                 | Core need                                                                                                          | Key constraints                                                                            |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------ |
| **P1 — Meera, 72, polypharmacy patient**           | Takes 7 medications on 3 schedules; mild visual impairment; uses a weekly pill organizer her daughter fills | "Is this handful the right pills for tonight?"                                                                     | Large text, high-contrast UI, voice feedback, one-tap flow, tremor-tolerant capture        |
| **P2 — Anil, 45, remote caregiver**                | Meera's son, lives in another city; fills her pill organizer monthly; worries between visits                | Visibility into missed/mismatched doses; alerts on repeated mismatches                                             | Opt-in sharing only; summary not surveillance; respects Meera's autonomy                   |
| **P3 — Sarah, 34, chronic-condition self-manager** | Takes 3 daily meds; generics change appearance every refill                                                 | Quick sanity check when the pharmacy swaps manufacturers ("this pill looks different — is it still my metformin?") | Speed (< 5 s end-to-end); minimal friction; identify-only mode without a schedule          |
| **P4 — Devon, home-health aide**                   | Administers meds to multiple clients per day                                                                | Fast per-client verification and an audit trail of administered doses                                              | Multi-profile switching; exportable log; offline operation in homes with poor connectivity |


**Persona → feature mapping**


| Feature                               | P1               | P2                   | P3    | P4    |
| ------------------------------------- | ---------------- | -------------------- | ----- | ----- |
| Verify dose (camera → match/mismatch) | ●core            |                      | ●core | ●core |
| Identify-only mode (no schedule)      | ○                |                      | ●core | ○     |
| Schedule & regimen management         | ●core (assisted) | ●core (remote setup) | ●     | ●     |
| Caregiver sharing & alerts            | ○ (subject)      | ●core                |       |       |
| Multi-profile + audit log export      |                  | ○                    |       | ●core |
| Accessibility (voice, large UI)       | ●core            |                      |       | ○     |


● = primary, ○ = secondary

---



## 5. User Stories

**Verification (core)**

- As a polypharmacy patient, I want to point my camera at the pills in my palm and hear/see whether they match tonight's dose, so that I don't take the wrong medication. (P0)
- As a patient, I want the app to tell me clearly when it *cannot* identify a pill and what to do next (retake, better light, check with pharmacist), so that I'm never given a false guarantee. (P0)
- As a self-manager, I want to identify an unknown pill without any schedule configured, so that I can check a refill that looks different. (P0)
- As a patient with shaky hands, I want the app to auto-capture when the image is good enough instead of making me press a button at the right moment. (P1)

**Schedule setup**

- As a patient or caregiver, I want to add a medication by photographing the prescription label or typing its name, and confirm the expected pill appearance from a reference image, so setup takes minutes not hours. (P0 manual / P1 label-OCR)
- As a caregiver, I want to set up and edit my parent's regimen remotely, so that she only has to point and shoot. (P1)

**History & sharing**

- As a caregiver, I want an opt-in daily summary and an alert after N consecutive mismatches/misses, so that I can intervene early without hovering. (P1)
- As a home-health aide, I want a timestamped log of verified administrations per client that I can export, so that I have an audit trail. (P1)

**Edge cases**

- As a user, when two pills in my regimen look nearly identical, I want the app to explicitly say "visually ambiguous — verify by imprint" rather than guess. (P0)
- As a user with no network connection, I want verification to work fully offline. (P0)
- As a user, when the pill is a half-tablet (split), I want the app to flag reduced confidence rather than misidentify. (P1)

---



## 6. Core Functionality Overview

```
┌────────────────────────────────────────────────────────────────┐
│                        PillCheck v1                            │
├───────────────┬───────────────────┬────────────────────────────┤
│ F1 Capture &  │ F2 Recognition    │ F3 Verification &          │
│    Guardrails │    Pipeline       │    Decision Engine         │
│ guided overlay│ detect → segment  │ schedule lookup, match     │
│ quality gates │ → embed → OCR →   │ logic, calibrated          │
│ auto-capture  │ fuse → rank       │ abstention, result UX      │
├───────────────┼───────────────────┼────────────────────────────┤
│ F4 Regimen    │ F5 History &      │ F6 Reference Library       │
│    Management │    Sharing        │ curated pill DB (embeddings│
│ meds, doses,  │ dose log, export, │ + metadata), on-device     │
│ schedules     │ caregiver alerts  │ index, update mechanism    │
└───────────────┴───────────────────┴────────────────────────────┘
```

---



## 7. Functional Requirements



### P0 — Must Have

**FR-1 Guided capture with quality gates**

- Live overlay guiding pill placement region and distance; real-time checks: blur (Laplacian variance ≥ threshold), exposure (histogram clipping < threshold), minimum effective resolution of pill region.
- Capture is blocked with a specific corrective prompt ("Move closer", "More light") until gates pass; auto-capture fires when all gates pass for 500 ms.
- *Acceptance:* Given poor lighting, when the user aims at a pill, then the shutter does not fire and the app shows the specific correction; given adequate conditions, capture occurs without a button press within 2 s.

**FR-2 Pill detection & segmentation (multi-pill)**

- Detect 1–8 pills per frame; segment each from the background before recognition.
- *Acceptance:* On the internal multi-pill test set, detection recall ≥ 95% and precision ≥ 95% at IoU 0.5; overlapping pills are either separated or flagged "spread pills apart".

**FR-3 Fine-grained pill recognition**

- Per segmented pill: visual embedding (metric-learned) matched against the on-device reference index; imprint OCR on the crop; late fusion re-ranks candidates by combining embedding similarity with imprint match against the NDC imprint field.
- Output: ranked candidate list with calibrated confidence per pill.
- *Acceptance:* ≥ 95% top-1 on curated regimen sets (≤ 15 candidate meds per user); report top-1/top-5 on ePillID consumer holdout with comparison to the published metric-learning baseline.

**FR-4 Verification decision engine**

- Inputs: recognized pill IDs + confidences, active user, current time, regimen. Outputs exactly one of: **MATCH** (all expected pills present, nothing unexpected), **MISMATCH** (unexpected pill or wrong count, with per-pill explanation), **CANNOT IDENTIFY** (below threshold → guidance).
- Confidence thresholds tuned so that P(wrong pill shown as MATCH) < 0.5%; ambiguity rule: if top-2 candidates within a similarity margin and imprint unresolved → CANNOT IDENTIFY, never a guess.
- Wrong-time handling: right pill outside its dose window → distinct "right pill, wrong time" state.
- *Acceptance (Given/When/Then):* Given tonight's dose is Pill A + Pill B, when the user shows A + C, then result is MISMATCH identifying C as unexpected and B as missing; given an unreadable blister-crushed pill, then result is CANNOT IDENTIFY with retake guidance — never MATCH.

**FR-5 Regimen management (manual)**

- CRUD for medications: name, NDC (optional), expected appearance (chosen from reference images), dose count, schedule windows; support ≥ 15 active medications, ≥ 4 dose windows/day.
- *Acceptance:* A new user can configure a 5-medication regimen in < 10 minutes; each medication is linked to exactly one reference appearance record (both sides).

**FR-6 Identify-only mode**

- Camera flow without schedule context; returns top-3 candidates with reference images and confidence; explicit "not a medical confirmation" framing.

**FR-7 Offline operation & on-device inference**

- All capture, inference, and verification run without network; models bundled or downloaded once; reference index stored locally.
- *Acceptance:* Airplane-mode E2E verification succeeds; no image payload appears in any network log in default mode.

**FR-8 Result presentation & accessibility**

- Full-screen color-coded result (green/red/amber) + icon + text; optional voice announcement; all text ≥ WCAG AA contrast; primary flow operable with one hand and ≤ 2 taps.

**FR-9 Dose event logging**

- Every verification attempt logged locally: timestamp, profile, result, per-pill candidates/confidence, image quality metrics. Images stored only if the user opts in (for personal reference / model improvement consent).



### P1 — Should Have

- **FR-10** Prescription-label OCR to pre-fill medication setup (name, strength, sig), user-confirmed before save.
- **FR-11** Caregiver link: invited account gets remote regimen editing + daily summary + alert after N consecutive misses/mismatches. Subject can revoke anytime; sharing state always visible to the subject.
- **FR-12** Multi-profile support with fast switcher and per-profile CSV/PDF log export (aide use case).
- **FR-13** Refill-appearance-change flow: when a recognized pill matches the *drug* (via NDC family) but not the stored appearance, offer "update expected appearance" instead of a hard mismatch.
- **FR-14** Personal few-shot enrollment: user captures 3–5 photos of an unrecognized/local-market pill to add a private reference entry (embeddings computed on device).



### P2 — Future Considerations (design for, don't build)

- Pharmacy/EHR integration (FHIR MedicationRequest) — keep NDC as the primary med key now.
- Drug-interaction warnings — regimen schema keeps normalized drug identifiers.
- Smart-dispenser / pillbox hardware integration.
- Ingestion confirmation mode.
- Clinical-trial/e-DOT deployment profile.

---



## 8. Non-Functional Requirements


| Category               | Requirement                                                              | Target                                                                                                                                                                                               |
| ---------------------- | ------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Latency**            | Capture-to-result, on-device, mid-range phone (e.g., 4-year-old Android) | ≤ 3 s p50, ≤ 6 s p95                                                                                                                                                                                 |
| **Model footprint**    | Total bundled models (detector + encoder + OCR)                          | ≤ 150 MB; INT8/FP16 quantized                                                                                                                                                                        |
| **Accuracy / safety**  | False MATCH rate at operating point                                      | < 0.5% (primary safety metric — optimize abstention before accuracy)                                                                                                                                 |
| **Availability**       | Core verification                                                        | 100% offline-capable; no server dependency in the loop                                                                                                                                               |
| **Privacy**            | Image handling                                                           | On-device inference; images never uploaded by default; opt-in contribution is explicit, revocable, and separately consented                                                                          |
| **Security**           | Local data                                                               | Health data (regimen, logs) encrypted at rest (platform keystore); caregiver sync channel E2E-encrypted; no third-party analytics on health events                                                   |
| **Compliance posture** | Positioning                                                              | Prominent "assistive tool, not a medical device; confirm with your pharmacist" disclaimer on first run and in every CANNOT IDENTIFY result; HIPAA-adjacent hygiene even though v1 is consumer-direct |
| **Accessibility**      | UI                                                                       | WCAG 2.1 AA; screen-reader labels on all controls; voice output for results; min touch target 48dp                                                                                                   |
| **Robustness**         | Environment                                                              | Maintain targets across: indoor warm/cool lighting, daylight, common countertop backgrounds, hand-held pills; degrade to abstention (never to silent errors) outside envelope                        |
| **Reproducibility**    | Engineering                                                              | Deterministic training configs, pinned deps, DVC (or equivalent) for data versions, eval scripts that regenerate every reported number                                                               |
| **Observability**      | Product analytics (non-image)                                            | Anonymous funnel + result-distribution metrics, opt-out; no PII, no images                                                                                                                           |


---



## 9. User Flows



### UF-1: Verify a scheduled dose (happy path — P1/P3)

```
Open app ─► [Active dose window?] ─yes─► "Verify tonight's dose (A + B)" CTA
   │                                            │
   no ─► Home (next dose shown)                 ▼
                                        Camera + overlay
                                                │  quality gates pass
                                                ▼
                                        Auto-capture ─► on-device pipeline (≤3s)
                                                │
                                        ┌───────┴────────┐
                                        ▼                ▼
                                    MATCH (green)    see UF-2/UF-3
                                        │
                                        ▼
                              "Take your dose" + log event ─► Done
```



### UF-2: Mismatch path

```
Result: MISMATCH (red)
  ├─ Per-pill breakdown: "Found Lisinopril 10mg — not scheduled now.
  │   Missing: Metformin 500mg."
  ├─ Actions: [Rescan] [This is correct — update schedule?] [Call pharmacist]
  └─ Event logged as mismatch; caregiver alert counter increments (if linked)
```



### UF-3: Cannot-identify path (safety-critical UX)

```
Result: CANNOT IDENTIFY (amber)
  ├─ Reason surfaced: "Imprint not readable" / "Two look-alike candidates"
  ├─ Guidance: retake with flip-to-other-side prompt, lighting tip
  ├─ After 2 failed retakes: "Verify manually — check imprint '<expected>'
  │   against your pill; when in doubt ask your pharmacist." [Mark taken manually]
  └─ Never auto-resolves to MATCH
```



### UF-4: First-run regimen setup (P0 manual / P1 OCR-assisted)

```
Onboarding ─► disclaimer + privacy explainer ─► Add medication
   ├─ (P1) Photograph label ─► OCR pre-fill ─► user confirms
   ├─ (P0) Type name ─► pick strength/form ─► shown reference image(s)
   │        "Does your pill look like this?" ─► confirm / pick alternative
   ├─ Set dose count + schedule windows
   └─ Repeat per medication ─► Home
```



### UF-5: Caregiver link (P1)

```
Patient: Settings ─► Share with caregiver ─► QR/invite code
Caregiver app: accept ─► scoped access (regimen edit + summaries)
Ongoing: daily digest; alert if ≥N consecutive missed/mismatched doses
Patient: banner shows active sharing; one-tap revoke
```

---



## 10. System & Data Flow



### 10.1 Inference data flow (on-device)

```
Camera frames
   │
   ▼
[F1 Quality gates] ──fail──► corrective prompt (loop)
   │ pass
   ▼
Captured frame
   │
   ▼
[Detector: YOLO-family, fine-tuned] ─► N pill bboxes
   │
   ▼
[Segmentation: lightweight mask head / SAM-distilled] ─► N masked crops
   │
   ├───────────────────────────────┐
   ▼                               ▼
[Embedding encoder                [Imprint OCR
 (timm backbone + metric head,     (PaddleOCR-mobile / TrOCR-small)
 ArcFace-trained)]                 → imprint string + confidence]
   │                               │
   ▼                               │
[ANN lookup vs. on-device          │
 reference index (FAISS/HNSW)]     │
   │  top-k candidates             │
   └──────────────┬────────────────┘
                  ▼
        [Late fusion re-ranker]
        score = α·embed_sim + β·imprint_match(NDC imprint field)
                  │
                  ▼
        [Calibrated confidence (temperature-scaled)
         + ambiguity margin test]
                  │
                  ▼
        [Decision engine: regimen × time × candidates]
                  │
                  ▼
        MATCH / MISMATCH / CANNOT IDENTIFY  ─► UI + local event log
```



### 10.2 Training/data pipeline (offline, repo)

```
Raw sources ─► ingest & normalize ─► split registry (by pill type, not image)
   │                                      │
   ▼                                      ▼
Augmentation policy (consumer-domain      Train: detector │ encoder (metric) │ OCR fine-tune
simulation: color jitter, blur, JPEG,     │
shadows, perspective, background paste)   ▼
   │                                Eval harness: ePillID protocol + internal
   ▼                                consumer set + safety metrics (false-MATCH)
Reference index build (embed all          │
reference images ─► FAISS index +         ▼
metadata sidecar) ─► versioned artifact   Export: ONNX ─► TFLite/CoreML (INT8)
                                          ─► bundled into app + demo (Gradio)
```



### 10.3 Data at rest (device)

```
SQLite (encrypted)                      Files
├─ profiles                             ├─ models/ (versioned, hash-pinned)
├─ medications ──┐                      ├─ ref_index/ (FAISS + metadata)
├─ schedules ────┼─ FK: profile_id      └─ opt_in_images/ (only with consent)
├─ dose_events ──┘  FK: medication_id
└─ caregiver_links (tokens, scopes)
```

---



## 11. Data Requirements & Mappings



### 11.1 Datasets


| Dataset                                      | Role                                                                                   | Size / notes                                                                                                                                       | Access                                                     |
| -------------------------------------------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| **ePillID** (NIH-derived benchmark)          | Primary train/eval for fine-grained recognition; published baseline to compare against | ~13k images, 9,804 appearance classes (two sides × 4,902 pill types); mixes controlled reference images with real-world consumer images; low-shot  | Public — `usuyama/ePillID-benchmark` (GitHub)              |
| **NLM C3PI reference images**                | Reference library seed (clean canonical appearance per pill)                           | ~4,000 controlled-lighting reference images (6.8 GB)                                                                                               | Public — data.gov                                          |
| **NDC/Pillbox metadata**                     | Imprint text, shape, color, size, drug identity per pill                               | Tabular; joins to images via NDC                                                                                                                   | Public (FDA NDC directory + archived Pillbox data)         |
| **Internal multi-pill set** (self-collected) | Detector/segmentation training + realistic multi-pill eval; portfolio differentiator   | Target ≥ 500 photos: OTC pills in hands/organizers/counters, varied lighting; annotate boxes+masks (CVAT/Label Studio); double-annotate 10% for QA | Self-collected; OTC only (no prescription handling issues) |
| **Hard-negative look-alike pairs**           | Threshold tuning for the ambiguity rule                                                | Curated from ePillID confusion matrix                                                                                                              | Derived                                                    |




### 11.2 Entity model & field mappings

**Medication (per profile)**


| Field                     | Type                     | Source / mapping                                                                                        |
| ------------------------- | ------------------------ | ------------------------------------------------------------------------------------------------------- |
| med_id                    | UUID                     | app                                                                                                     |
| profile_id                | FK                       | app                                                                                                     |
| drug_name, strength, form | text                     | user input / label OCR ↔ NDC directory `PROPRIETARYNAME`, `ACTIVE_NUMERATOR_STRENGTH`, `DOSAGEFORMNAME` |
| ndc                       | text (nullable)          | NDC directory `NDCPACKAGECODE` — primary external key (P2 integrations hang off this)                   |
| appearance_ref_ids[2]     | FK → ReferenceAppearance | chosen at setup (front/back)                                                                            |


**ReferenceAppearance (bundled library + private few-shot entries)**


| Field                                  | Type                         | Source                                                                         |
| -------------------------------------- | ---------------------------- | ------------------------------------------------------------------------------ |
| ref_id                                 | UUID                         | build pipeline                                                                 |
| ndc                                    | text                         | C3PI/Pillbox metadata                                                          |
| side                                   | enum(front, back)            | dataset                                                                        |
| embedding                              | float[D]                     | encoder output (index sidecar)                                                 |
| imprint, shape, color, size_mm, scored | text/enum/float              | Pillbox/NDC fields `SPLIMPRINT`, `SPLSHAPE`, `SPLCOLOR`, `SPLSIZE`, `SPLSCORE` |
| image_uri                              | path                         | bundled asset                                                                  |
| origin                                 | enum(library, user_enrolled) | app                                                                            |


**DoseEvent**


| Field                    | Type                                                 | Notes                                                                    |
| ------------------------ | ---------------------------------------------------- | ------------------------------------------------------------------------ |
| event_id, profile_id, ts | UUID/FK/datetime                                     |                                                                          |
| scheduled_window_id      | FK (nullable)                                        | null for identify-only                                                   |
| result                   | enum(match, mismatch, cannot_identify, manual_taken) |                                                                          |
| per_pill[]               | JSON                                                 | {bbox, top_k:[{ref_id, embed_sim, imprint_conf, fused_score}], decision} |
| quality                  | JSON                                                 | blur/exposure/resolution metrics — feeds abstention analysis             |
| image_uri                | path (nullable)                                      | only with explicit opt-in                                                |




### 11.3 Data governance

- OTC-only self-collection; no photographing of other people's prescriptions.
- Opt-in contributed images: separate consent screen, purpose-limited (model improvement), deletable, never bundled with identity beyond a random contributor ID.
- Dataset licenses verified for redistribution before bundling reference images (NIH data is public; record license notes in repo).
- Train/val/test splits stratified **by pill type** (no appearance-class leakage across splits).

---



## 12. Technical Specifications (implementation notes)


| Component            | Choice                                                                                                            | Rationale / trade-off (recorded per decision-log practice)                                                 |
| -------------------- | ----------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Language / framework | Python 3.11, PyTorch 2.x                                                                                          | ecosystem; export path to mobile                                                                           |
| Detection            | Ultralytics YOLOv8/11-n or -s, fine-tuned on internal multi-pill set                                              | speed/size on-device; trade-off: license (AGPL) — alternative RT-DETR if licensing matters for reuse       |
| Segmentation         | YOLO-seg head (preferred) or distilled SAM                                                                        | full SAM too heavy for the 150 MB budget                                                                   |
| Encoder              | timm ConvNeXt-T / EfficientNetV2-S + embedding head, ArcFace loss (`pytorch-metric-learning`)                     | metric learning ⇒ add new pill = add one embedding, **no retraining** — key operational decision           |
| Retrieval            | FAISS (flat for regimen-scoped ≤ 15 classes; HNSW for full-library identify mode)                                 | regimen scoping slashes the effective search space and error rate                                          |
| OCR                  | PaddleOCR mobile models (fallback: TrOCR-small)                                                                   | imprint = tiny, embossed, curved text; expect low recall — that's why fusion is late/soft, not a hard gate |
| Fusion               | weighted score + imprint edit-distance vs. NDC `SPLIMPRINT`; weights tuned on val                                 | simple, inspectable, debuggable — chosen over learned fusion for v1 explainability                         |
| Calibration          | temperature scaling + top-2 margin abstention                                                                     | directly serves the < 0.5% false-MATCH NFR                                                                 |
| Export               | ONNX → TFLite (Android) / CoreML (iOS), INT8 PTQ with per-channel quant; accuracy delta budget ≤ 1 pt             | footprint + latency targets                                                                                |
| Demo (portfolio)     | Gradio web demo (server-side inference) + Android reference app                                                   | Gradio proves the pipeline publicly; the app proves on-device claims                                       |
| Repo infra           | Git + DVC, pinned env (uv/conda-lock), Dockerfile, Makefile targets for every reported metric, `DECISIONS.md` log | end-to-end criterion; reviewer reproducibility                                                             |


---



## 13. Success Metrics

**Leading (model/product, evaluable at each phase)**


| Metric                                                                  | Success                              | Stretch      | Method                                                                                                                           |
| ----------------------------------------------------------------------- | ------------------------------------ | ------------ | -------------------------------------------------------------------------------------------------------------------------------- |
| ePillID consumer holdout top-1 / top-5                                  | ≥ published metric-learning baseline | +3 pts top-1 | eval harness, fixed protocol                                                                                                     |
| Regimen-scoped verification top-1 (≤15 candidates)                      | ≥ 95%                                | ≥ 98%        | internal consumer set                                                                                                            |
| False-MATCH rate @ operating threshold                                  | < 0.5%                               | < 0.1%       | hard-negative + full test sweep                                                                                                  |
| Abstention rate on in-envelope images                                   | ≤ 15%                                | ≤ 8%         | (too-high abstention = unusable; tension with false-MATCH is the central tuning trade-off — document the chosen operating point) |
| E2E latency, mid-range Android                                          | p50 ≤ 3 s                            | p50 ≤ 1.5 s  | on-device benchmark script                                                                                                       |
| Task completion in hallway usability test (n≥8, incl. 60+ participants) | ≥ 85%                                | ≥ 95%        | scripted tasks UF-1–UF-4                                                                                                         |


**Lagging (if released publicly)**


| Metric                                                                                | Target                                     |
| ------------------------------------------------------------------------------------- | ------------------------------------------ |
| 30-day retention of users with a configured regimen                                   | ≥ 25%                                      |
| Verifications per active user per week                                                | ≥ 5                                        |
| % of mismatch events followed by a corrected action (rescan → match, or schedule fix) | ≥ 60%                                      |
| GitHub engagement (portfolio proxy)                                                   | 100+ stars / cited in a pill-ID discussion |


---



## 14. Timeline & Phasing


| Phase                     | Scope                                                                                                              | Exit criteria                                                       | Est. effort (solo, part-time) |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------- | ----------------------------- |
| **0 — Foundations**       | Repo scaffolding, data ingest (ePillID + C3PI + NDC join), eval harness reproducing the ePillID baseline protocol  | Baseline numbers reproduced ±1 pt                                   | 2 wks                         |
| **1 — Recognition core**  | Encoder + metric training, FAISS index, fusion with OCR, calibration/abstention; Gradio demo (single pill, upload) | G1 model metrics met on ePillID; demo live                          | 4 wks                         |
| **2 — Real-world layer**  | Self-collected multi-pill dataset, detector+seg fine-tune, capture guardrails, consumer-domain augmentation        | FR-2 targets; internal consumer-set metrics                         | 4 wks                         |
| **3 — Product v1**        | Decision engine, regimen mgmt, offline app (Android reference), logging, accessibility pass, disclaimers           | All P0 FRs accepted; NFR latency/footprint met; usability test done | 5 wks                         |
| **4 — Fast follows (P1)** | Label OCR setup, caregiver link, multi-profile/export, few-shot enrollment                                         | Per-FR acceptance                                                   | as capacity allows            |


Dependencies: none external (all public data). Hard deadline: none — phase exits gate progression.

---



## 15. Risks & Mitigations


| Risk                                                               | Likelihood | Impact        | Mitigation                                                                                                             |
| ------------------------------------------------------------------ | ---------- | ------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Imprint OCR recall too low on consumer photos                      | High       | Med           | Fusion is soft (embedding carries the load); flip-side prompt in UF-3; report OCR contribution ablation honestly       |
| Look-alike pills within one user's regimen                         | Med        | High (safety) | Ambiguity margin → forced abstention; setup-time warning when a user adds two visually confusable meds                 |
| Generic appearance changes on refill outpace the reference library | High       | Med           | FR-13 appearance-update flow + FR-14 few-shot enrollment                                                               |
| On-device budget forces accuracy loss                              | Med        | Med           | Quantization delta budget ≤ 1 pt enforced in CI eval; fall back to FP16 if breached                                    |
| Perceived medical-device scope creep                               | Low        | High          | Non-goals + persistent disclaimer language; verification framed as assistive check, ingestion/clinical claims excluded |
| Self-collected dataset too small for detector robustness           | Med        | Med           | Synthetic compositing (paste segmented ePillID pills onto household backgrounds) to multiply effective data            |


---



## 16. Open Questions


| #   | Question                                                                                                              | Owner                    | Blocking?                   |
| --- | --------------------------------------------------------------------------------------------------------------------- | ------------------------ | --------------------------- |
| Q1  | Android-first only for v1, or Gradio-web + Android? (iOS/CoreML doubles export work)                                  | Q (product)              | Yes — decide before Phase 3 |
| Q2  | YOLO (AGPL) acceptable for an open-source portfolio repo, or switch to RT-DETR/DETR-family?                           | Q (eng/legal-lite)       | Before Phase 2              |
| Q3  | Exact abstention operating point: what false-MATCH vs. abstain-rate pair do target users tolerate?                    | Usability test (Phase 3) | No — tune during Phase 3    |
| Q4  | Caregiver sync transport for P1: self-hosted lightweight backend vs. E2E over an existing channel?                    | Q (eng)                  | No — P1 only                |
| Q5  | Should identify-only mode search the full 4.9k-type library on-device, or a top-N common-meds subset to hold latency? | Eng benchmark (Phase 2)  | No                          |


---



## 17. Out-of-Scope Parking Lot

Interaction checking · FHIR/pharmacy sync · ingestion confirmation · smart dispenser hardware · counterfeit detection · non-solid dose forms · clinical-trial deployment profile · insurance/payer reporting.

---



## Appendix A — Competitive Context (from research)


| Player                             | What it does                                                                                                       | Gap PillCheck fills                                                       |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------- |
| Medisafe                           | Reminder/management platform, 10M+ users; no camera verification                                                   | Visual verification of the actual pill                                    |
| AiCure Patient Connect             | CV-based dosing confirmation for clinical trials; facial-recognition workflow; reported as cumbersome for patients | Consumer-grade, lightweight, privacy-first (no face video), open-source   |
| Drugs.com / WebMD pill identifiers | Manual attribute entry (shape/color/imprint typed by user)                                                         | Fully visual, automatic, schedule-aware                                   |
| ePillID research baselines         | Single-pill recognition benchmark, no product layer                                                                | End-to-end product: multi-pill, decision engine, on-device, abstention UX |




## Appendix B — Reference Links

- ePillID benchmark & code: github.com/usuyama/ePillID-benchmark
- NLM C3PI reference images: catalog.data.gov (Computational Photography Project for Pill Identification)
- FDA NDC Directory (imprint/shape/color metadata source)

