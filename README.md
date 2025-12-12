# Table of Contents

---

## 0. Executive Summary (One Page)

**What this repository is:**
A reproducible, cross-platform system that turns power-law and fractal claims into executable, testable models — separating theory, measurement, and validation in a way that directly operationalizes ideas discussed in Veritasium’s *Power Laws* video.

**What it demonstrates immediately:**
Running one command produces a single HTML report showing raw data, log–log scatter plots, theoretical expectations, fitted results, and residuals — across multiple classic systems (Zipf, earthquakes, networks, fractals).

**Why it exists:**
To move the conversation from “this looks like a straight line” to “this theory survives noise, cutoffs, discretization, and independent implementations.”

---

## 1. From the Video to a Testable Claim

**Context:**
Veritasium’s video shows how diverse phenomena collapse to straight lines in log–log space, but also highlights that real data is noisy, finite, and messy.

**Core observation:**
The straight line is not the phenomenon — it is a fixed point. The phenomenon is the distribution of observations *around* that fixed point.

**What this repo does differently:**
It encodes that distinction directly: theory as fixed points, data as neighborhoods, and validation as computed geometry — not just plots.

---

## 2. What You See When You Run It (Evidence First)

**Immediate outcome:**
Running `start.sh → Run ALL Platform Tests` generates a single self-contained HTML report.

**What’s in the report:**

* Raw and derived values for each system
* Log–log scatter plots with theoretical slope overlays
* Observed vs expected behavior
* Fit quality metrics and residuals
* Clear pass/fail validation across platforms

**Why this matters:**
The report is not illustrative — it is the primary artifact. Everything else in the repo exists to make that report trustworthy.

*(Link to example report if hosted)*

---

## 3. Systems Modeled (Why These Examples)

**Included systems:**
Fractals (Sierpinski, Koch) and statistical power laws (Zipf, earthquakes, forest fires, sandpiles, scale-free networks).

**Why these were chosen:**
They span geometric vs statistical systems, clean vs noisy domains, and are all explicitly discussed (or implied) in the video.

**Unifying idea:**
Despite wildly different mechanisms, all are evaluated using the same log–log machinery, under the same validation rules.

---

## 4. How the Repo Operationalizes the Video’s Ideas

**Fixed points:**
Each system declares a theoretical log–log slope — the claim being tested.

**Neighborhoods:**
Observed data (idealized or noisy) lives separately, with explicit measurement assumptions.

**Validation:**
Fits, residuals, slope deltas, and confidence metrics are computed automatically and stored — not eyeballed.

**Result:**
You can ask, in a concrete way: *How close is reality to the theory, under stated assumptions?*

---

## 5. Single Source of Truth (Why This Is Reproducible)

**The ERB (Entity Rule Book):**
All systems, fields, formulas, and dependencies are defined once in a canonical JSON specification.

**What this enables:**

* Identical computation across languages
* Explicit dependency graphs
* No “hidden math” in notebooks or scripts

**Key distinction:**
This is not data duplicated across implementations — it is logic generated from one source.

---

## 6. Cross-Platform Computational Engines

### 6.1 Python Engine

Pure Python, lazy evaluation, no external dependencies. Serves as the canonical generator and validator.

### 6.2 PostgreSQL Engine

Normalized tables with computed views and SQL functions. Demonstrates that the same math works inside a database.

### 6.3 Go Engine

Strongly typed, compiled implementation. Demonstrates portability and numerical consistency outside scripting environments.

**Why three engines:**
If a scaling law is real, it should not depend on the language used to compute it.

---

## 7. The Test Regime (Why the Results Are Credible)

**Generated test artifacts:**

* Base data (known-good values)
* Test input (raw facts only)
* Answer key (canonical expected outputs)

**What’s being tested:**
That each engine independently reconstructs all derived values within a strict tolerance.

**Why this matters:**
This turns scaling claims into something closer to hardware verification than data visualization.

---

## 8. Measurement Models and Regimes (Where Reality Enters)

**Measurement models:**
Noise, cutoffs, and discretization are explicitly defined — not hand-waved.

**Scale regimes:**
Different slope behaviors over different scale ranges can be declared and tested.

**Implication:**
The repo is designed to surface where and why scaling laws break, not just where they work.

---

## 9. Extending the System

**Adding a new dataset:**
Define the system, load observations, run inference — no bespoke analysis code required.

**Swapping domains:**
The same machinery applies to linguistics, networks, physics, economics, or anywhere scaling is claimed.

---

## 10. Conclusion

**What this is not:**
Not a proof of universality. Not a visualization project. Not a one-off analysis.

**What it is:**
A concrete, reproducible way to test scaling claims — using the exact issues raised in the video — and to make those tests portable, inspectable, and falsifiable.

**Why this might be worth a follow-up video:**
It shows what happens when “that straight line” is treated not as an endpoint, but as the beginning of a scientific workflow.

---

## 0. Executive Summary

This repository turns power-law and fractal claims into **executable, testable models**.

It implements a single, canonical specification for scaling systems and uses it to generate **independent computational engines** (Python, PostgreSQL, and Go). One command runs all engines, compares their results against a shared answer key, and produces a **single self-contained HTML report** with raw values, log–log scatter plots, theoretical expectations, fitted results, and residuals.

The purpose is not to argue that power laws exist. It is to show **how scaling claims can be represented, tested, and validated** under explicit assumptions about noise, finite ranges, and measurement — the exact issues raised in Veritasium’s *Power Laws* video.

If the same scaling claim survives:

* noisy observations,
* finite cutoffs,
* multiple scale regimes,
* and independent implementations,

then it is at least operationally well-posed. If it fails, the failure is visible and localizable.

---

## 1. From the Video to a Testable Claim

Veritasium’s video makes a central move:
take data spanning many orders of magnitude, transform to log–log space, and a straight line appears.

That move is powerful — but incomplete.

The straight line is not the phenomenon.
It is a **fixed point**: a compact theoretical summary of expected behavior.
The real phenomenon is the **distribution of observations around that line**, including:

* finite-size effects,
* censoring and cutoffs,
* discretization,
* noise,
* and regime changes.

Most discussions stop at “the data looks linear.”
This repository starts where that discussion should continue.

It asks a stricter question:

> Given a stated theoretical slope, how does observed data actually cluster around it, and how stable is that conclusion under realistic measurement conditions?

To answer that, theory, data, and validation must be separated — not blended into a single plot.

---

## 2. What You See When You Run It (Evidence First)

Running the repository is intentionally simple:

```
./start.sh
→ Run ALL Platform Tests
```

This produces **one HTML file**.

That file is the primary artifact.

It contains, for each modeled system:

* raw and derived numerical values,
* log–log scatter plots of scale vs measure,
* the theoretical slope overlaid,
* fitted slopes from observed data,
* residuals and fit-quality metrics,
* and explicit pass/fail validation across platforms.

Nothing in the report is decorative.
Every value shown is either:

* a raw input,
* a mechanically derived quantity,
* or the output of a declared inference step.

If something is wrong, it shows up as:

* a numerical mismatch,
* a degraded fit,
* or a visible deviation in log–log space.

The rest of the repository exists to make this report **trustworthy and reproducible**.

---

## 3. Systems Modeled (Why These Examples)

The repository models a small set of canonical systems:

* **Geometric fractals**
  Sierpinski triangle, Koch snowflake

* **Statistical power laws**
  Zipf word frequencies
  Earthquake energies
  Forest fire sizes
  Sandpile avalanches
  Scale-free network degrees

These were chosen for three reasons:

1. They are explicitly discussed or strongly implied in the video.
2. They span both **idealized constructions** and **noisy empirical domains**.
3. They arise from very different mechanisms but are commonly described using the same log–log language.

All systems are evaluated using **the same machinery**:

* a declared theoretical log–log slope,
* observed data points (idealized or noisy),
* and a standardized validation pipeline.

This is intentional.

The repository is not comparing domains.
It is testing whether the *way we talk about scaling* can be made precise, portable, and falsifiable across domains.


## 4. How the Repo Operationalizes the Video’s Ideas

The core ideas in the video are not treated as metaphors here — they are encoded as structure.

**Fixed points (theory)**
Each system declares a single theoretical quantity: its expected slope in log–log space. This is the claim being tested, not inferred. It lives as data, not prose.

**Neighborhoods (observations)**
Observed values are stored separately from theory. They may be idealized or noisy, finite or truncated, discretized or continuous. The model does not assume cleanliness — it records assumptions explicitly.

**Validation (geometry, not vibes)**
Fitting, residuals, slope deviation, and fit quality are computed and stored as first-class outputs. Agreement is numeric and inspectable, not visual or rhetorical.

This directly mirrors the conceptual arc of the video:

* scaling laws as attractors,
* real data as imperfect realizations,
* and insight living in the *deviation structure*, not just the line.

---

## 5. Single Source of Truth (Why This Is Reproducible)

All logic in the repository originates from a single specification: an **Entity Rule Book (ERB)** JSON file.

That file defines:

* entities (systems, scales, observations, inference runs),
* field types (raw, lookup, calculated, aggregated),
* and the exact formulas linking them.

Nothing is “re-implemented by hand” in downstream code.

From this single source:

* Python classes are generated,
* PostgreSQL tables, functions, and views are created,
* Go structs and calculation chains are built.

The consequence is simple but important:

> If two implementations disagree, the disagreement is a bug — not an interpretation.

This removes an entire class of ambiguity that usually plagues cross-domain scaling discussions.

---

## 6. Cross-Platform Computational Engines

The same model is executed independently in three environments.

### Python

* Pure standard-library Python
* Lazy evaluation of derived values
* Serves as the canonical generator and validator

Python is used to generate test data, produce the answer key, and orchestrate validation.

### PostgreSQL

* Normalized tables store only raw facts
* All derived values are computed via SQL functions and exposed through views
* Demonstrates that the model works inside a database, not just scripts

This matters for real datasets that already live in relational systems.

### Go

* Strongly typed structs
* Explicit calculation order
* Compiled execution

Go provides an additional check: the math must survive strict typing and compilation.

The engines are not optimized for performance.
They are optimized for **agreement**.

---

## 7. The Test Regime (Why the Results Are Credible)

The repository includes an explicit, automated test protocol.

**Generated artifacts**

* **Base data**: known-good values used to initialize systems
* **Test input**: raw facts only (no derived fields)
* **Answer key**: canonical derived results for all fields

**What is tested**
Each engine must:

1. Load identical raw inputs
2. Compute all derived quantities using the declared formulas
3. Match the answer key within a fixed numeric tolerance

Fields validated include:

* scale construction,
* log transforms,
* fitted slopes,
* and other derived quantities.

**Why this matters**
This turns scaling claims into something closer to **numerical verification** than exploratory analysis.

The question is no longer:

> “Does this look like a power law?”

It becomes:

> “Does this implementation reproduce the same derived structure, under the same assumptions, as every other implementation?”

Only after that question is answered does interpretation make sense.

## 8. Measurement Models and Scale Regimes (Where Reality Enters)

Real-world data does not fail to follow power laws randomly — it fails *systematically*.

This repository treats those failure modes as **explicit model components**, not caveats.

**Measurement models** encode how data is produced or observed:

* noise type and magnitude (e.g. lognormal noise),
* finite-size cutoffs (minimum and maximum observable scales),
* discretization and rounding effects.

These parameters are stored alongside the data they affect, so deviations can be interpreted in context rather than dismissed as “messy data.”

**Scale regimes** allow a single system to declare multiple expected behaviors over different scale ranges:

* early vs mature scaling,
* power-law body vs finite-size cutoff,
* small-event vs large-event regimes.

This directly reflects what the video emphasizes but cannot formalize on screen:
that scaling behavior is often *local in scale*, not global.

The result is a system that does not just ask *whether* a power law fits, but *where*, *under what conditions*, and *how robustly*.

---

## 9. Extending the System (What This Is For)

The repository is structured so new data does not require new analysis code.

To evaluate a new scaling claim:

1. Define the system and its theoretical slope.
2. Load observed measurements (from any source).
3. Declare measurement assumptions if needed.
4. Run the inference and validation pipeline.

The same machinery applies whether the data comes from:

* published datasets,
* simulations,
* scraped empirical measurements,
* or future experiments.

Because theory, observation, and validation are already separated, new domains plug into an existing workflow rather than creating a bespoke one.

This is deliberate: the repo is meant to support *comparison across claims*, not just demonstration of individual ones.

---

## 10. Conclusion

This repository does not claim that power laws are universal.

It claims something narrower and more useful:

> Scaling laws can be represented as executable objects, tested under explicit assumptions, and validated across independent implementations.

The Veritasium video raises the right questions:

* Why do these patterns appear so often?
* How much trust should we place in straight lines on log–log plots?
* Where do these models break?

This project answers by building infrastructure, not arguments.

It shows what happens when:

* the straight line is treated as a hypothesis,
* deviations are treated as data,
* and reproducibility is treated as a requirement.

If power laws are as fundamental as they seem, they should survive this treatment.
If they are not, the failures will be visible — and informative.

That is the point of the repo.
