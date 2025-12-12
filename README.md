# From Veritasium’s Power Laws to a Working Lab: Fixed Points, Neighborhoods, and Log–Log Science

Halfway through Veritasium’s power-law video, there’s a familiar move: take a messy distribution, go to log–log space, and the curve becomes a straight line.

But the straight line isn’t the phenomenon. The phenomenon is the *cloud* around it: finite ranges, censoring, measurement noise, discretization, regime changes, and “toy model vs real world” mismatch. The line is the attractor; the data is the neighborhood.

So I built the thing I wished I had while watching: a repo where a power-law “theory” is a **row**, observations are a **neighborhood**, and validation is computed automatically.

This repo’s core is a CMCC model (and a PostgreSQL implementation of it) that treats scaling laws like executable science: define the fixed point, load the data, query the fit, and compare “what you expected” to “what you got.” 

---

## Power laws aren’t “a weird distribution.” They’re a different kind of world.

The video opens by contrasting normal distributions (heights, IQ, apple sizes) with power-law worlds—worlds where extreme events aren’t just possible, they’re structurally important.

In a normal distribution, the average is stable: outliers exist, but they don’t dominate the story. In a power-law distribution, outliers can dominate the average, and your intuition breaks: measuring more can increase your estimated “typical” value because the tail is heavy.

That difference isn’t just philosophical—it’s operational. If you’re playing a normal game, consistency wins. If you’re playing a power-law game, a small number of runaway outcomes can dominate everything.

And the central visual move is Pareto’s: take income distributions spanning orders of magnitude, log-transform them, and suddenly the story becomes a line with a slope. In the video’s framing, the exponent is the absolute value of that slope.

That’s the moment most people stop: “cool, it’s a line.”

But the interesting part is what *doesn’t* become a line: the ways real data deviates from the line, and what that deviation means.

---

## The missing piece: the *neighborhood*

The video keeps weaving between:

* **Toy mechanisms** (St. Petersburg paradox, sandpile rules, preferential attachment)
* **Empirical data** (income, earthquakes, forest fires, network degrees)
* **Big claims** (scale-free behavior, criticality, universality classes)

That weave is exactly why it’s compelling—and exactly why it’s hard to “do science” with it without constantly rewriting bespoke analysis scripts.

The repo’s premise is simple:

> A scaling theory is not just an equation. It’s a computational object that should be able to host many observations, tolerate noise, and report back how well reality clusters around it.

So the model makes a clean separation:

* **Fixed point (theory)**: the minimal parameters you’re claiming generate the scaling behavior.
* **Neighborhood (data)**: the actual observed points that orbit that theory in log–log space.
* **Inference (validation)**: the fitted slope/intercept and quality metrics that tell you whether the neighborhood actually clusters around the fixed point.

In this repo, that separation is not a metaphor. It’s schema.

---

## A schema for the video’s ideas

### Fixed points live in `systems`

Each “system” is a power-law or fractal instance with a theoretical slope (your fixed point in log–log geometry). In the included model, systems include Sierpinski, Koch, Zipf-like word frequencies, scale-free networks, sandpile avalanches, earthquakes, and forest fires, all unified with the same log–log machinery. 

The key field is:

* `systems.TheoreticalLogLogSlope`

This is the “one number” the video keeps returning to: the exponent that defines the straight line in log–log space.

### Neighborhoods live in `observed_scales`

The neighborhood is where reality shows up: noisy observations, finite ranges, discretization effects, etc. In the model, `observed_scales` mirrors the idealized `scales` table but explicitly represents measured data as its own dataset. 

Crucially, the model doesn’t just store `(Scale, Measure)`; it stores the transformations too:

* `observed_scales.LogScale`
* `observed_scales.LogMeasure`

That makes log–log space the “native geometry” of the entire system.

### Validation lives in `inference_runs`

This is where the repo turns “plot a line” into a reusable scientific primitive. For each system, `inference_runs` stores:

* `TheoreticalLogLogSlope` (the fixed point)
* `FittedSlope` (inferred from the neighborhood)
* `R2`, residual RMS, slope delta, and other fit metrics 

For example, the bundled data includes runs like:

* `ZipfWords_INF_OLS_LOG10`: theoretical slope -1, fitted slope about -0.965, high R²
* `ScaleFreeNet_INF_OLS_LOG10`: theoretical slope -2.5, fitted slope about -2.502, high R² 

So instead of “the line looks straight,” you can say: “here is the fitted slope, here is its deviation from theory, and here is the quality of fit.”

---

## Connecting the video’s greatest hits to the repo

### 1) Pareto / Zipf: “curve becomes line”

In the video, Pareto log-transforms income data, sees a line, and reads off a slope.

In this repo, that move becomes a standard workflow:

1. Define the theoretical slope for the system.
2. Load observed points.
3. Query the inference results.

Zipf-style behavior is represented directly as a system with a theoretical slope of -1 (`ZipfWords.TheoreticalLogLogSlope = -1`). 
The neighborhood is stored as noisy observed points (`ZipfWords_OBS_*`). 
The model then stores the reconstruction (fitted slope, intercept, R²) in `inference_runs`. 

That’s the video’s plot, but operational.

### 2) The St. Petersburg paradox: “two exponentials dancing”

The video shows how exponential payout growth and exponential probability decay combine to yield a power law.

This repo doesn’t hardcode that derivation; instead, it gives you a place to *host it*:

* the “theory” lives as the expected slope of the payout distribution in log–log space
* the “neighborhood” is your sampled realizations
* the “validation” is your recovered exponent and residual geometry

The important shift is that you’re not arguing about a line—you’re storing the claim and letting inference repeatedly re-derive it from realizations.

### 3) Self-organized criticality: “same process, all scales”

The video’s SOC arc (forest fires, sandpiles, earthquakes) is really about *regimes* and *cutoffs*—the parts that ruin simplistic “one slope fits all” takes.

This model makes those first-class:

* measurement models include cutoffs (`CutoffMinScale`, `CutoffMaxScale`) and noise (`NoiseSigma`) 
* there’s explicit scaffolding for multi-regime behavior via `scale_regimes` (e.g., “small fires” vs “large fires”) 

That matters because in the real world, scaling is often only “clean” over some span, and then something changes: finite-size effects, saturation, censoring, or a genuine crossover.

The repo isn’t just saying “power laws exist.” It’s giving you a place to say “power laws exist… *where* and *under what measurement assumptions*.”

---

## The best part: it’s executable

The CMCC model is accompanied by SQL that turns it into a working PostgreSQL database:

* raw, normalized tables (`systems`, `scales`, `observed_scales`, `inference_runs`, etc.) 
* calculation functions that mimic spreadsheet-like calculated fields 
* views that present “raw + computed” as a clean interface (like `vw_inference_runs`) 
* data inserts that load the example systems, points, and inference results 

That means the “instrument panel” is literally a query away: select from the views and you see, side by side, the fixed point and the inferred slope, plus fit quality.

---

## Why this is worth publishing

The video makes an emotional argument: power laws show up across wildly different domains, and that’s weird and important.

This repo makes a practical argument:

> If you want to take that seriously, you need a way to represent scaling claims that separates theory from measurement, and measurement from validation—without rewriting the world each time.

That’s what this does.

It doesn’t “prove universality.” What it does is make universality *testable in a reusable way*: add a system, load observations, compute slope, inspect residuals, compare regimes.

Power laws aren’t lines.

They’re neighborhoods around fixed points.

And once you build a place to store that distinction, you stop arguing about plots and start running experiments. 
