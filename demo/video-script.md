# Labwright Demo Video — Editor Script

## Context for editor

Labwright is a web app that generates hands-on SQL practice labs from any topic. The user picks skills, picks a theme (in this case "Gilmore Girls"), and AI generates a complete scenario with a storyline, sample data, a live database environment, and automated grading. The raw screen recording shows a full walkthrough of this flow.

The final video should feel like a punchy social media clip — fast cuts, big text overlays, cropped-in shots. Think "build in public" Twitter/LinkedIn energy, not a product tutorial.

**Target length:** 45–70 seconds
**Aspect ratio:** 9:16 (vertical, for Reels/TikTok/Shorts) OR 16:9 (horizontal, for Twitter/LinkedIn). If doing both, cut vertical first — it forces tighter crops.
**Resolution:** 1080x1920 (vertical) or 1920x1080 (horizontal)

---

## Raw footage you'll receive

One continuous screen recording of the app at ~1280x800. Key moments in the recording, in order:

1. Landing page (category grid)
2. Click into ETL Pipelines topic
3. Configure page — skill tags get clicked, difficulty selected
4. "Gilmore Girls" typed into custom theme field
5. "Generate Scenario" button clicked
6. Loading screen with terminal cursor + timer (2–5 min of real time)
7. Generated scenario appears — title, business context, source tables with data
8. "Open JupyterLab" clicked — Jupyter notebook visible
9. Back to app, "Check My Work" clicked
10. Validation results appear (pass/fail checks with AI feedback)

---

## Edit script

### BEAT 1 — Hook (0:00–0:03)

**What the viewer sees:** The generated scenario title/business context, cropped in tight so the text fills the screen. This is the OUTPUT — we show the payoff first.

**Text overlay (large, center):**
> what if Gilmore Girls was a SQL lab

**Crop/zoom:** 200–300% into the scenario title and first line of business context from the raw recording. Slow pan down. The text should reference Gilmore Girls / Stars Hollow / Luke's Diner — find the most entertaining line and feature it.

**Timing:** 3 seconds. This is the scroll-stopper — it needs to be immediately intriguing.

---

### BEAT 2 — Setup (0:03–0:08)

**What the viewer sees:** Quick cuts showing the input side of the app.

**Text overlay:**
> I built a tool that turns anything into a hands-on data lab

**Shots (fast cuts, ~1.5s each):**
1. Zoomed crop of the skill tags being selected (JOIN, AGGREGATION highlighted in teal)
2. Zoomed crop of "Gilmore Girls" being typed into the custom theme field

**Crop/zoom:** 200–250% on each element. Don't show the full browser — just the interactive element filling the frame.

---

### BEAT 3 — The generation (0:08–0:14)

**What the viewer sees:** The "Generate Scenario" button being clicked, then the loading screen.

**Shots:**
1. Zoomed crop of the teal "Generate Scenario" button, cursor clicks it (1.5s)
2. The loading screen with the terminal-style blinking cursor and timer. Speed this up 20–40x so the timer visibly counts up fast. (3–4s of screen time)

**Text overlay (appears over the sped-up loading):**
> AI builds the entire scenario from scratch

**Optional:** Add a subtle speed ramp indicator like "⚡ 30x" in the corner so viewers know it's sped up.

---

### BEAT 4 — The reveal (0:14–0:30)

This is the centerpiece. Slow down, let it breathe.

**Shot 1 (3s):** Zoomed crop of the generated scenario title. It should reference the Gilmore Girls theme. Slow Ken Burns pan.

**Text overlay:**
> complete storyline

**Shot 2 (3s):** Zoomed crop of the business context paragraph. Find the most fun sentence — something about Luke's Diner, Rory's reading list, Kirk's odd jobs, whatever the AI invented. Highlight or underline that sentence in post if possible.

**Text overlay:**
> real characters, real scenario

**Shot 3 (4s):** Zoomed crop of one source table showing sample data. The column headers and a few rows should be visible. The data will reference Gilmore Girls characters/places.

**Text overlay:**
> sample data that actually makes sense

**Shot 4 (3s):** Quick crop of the transformation steps / learning objectives. Don't need to read them, just show they exist.

**Text overlay:**
> step-by-step instructions

**Shot 5 (3s):** The JupyterLab notebook. Crop to show the notebook cells with the starter code. Shows it's a real environment, not a mockup.

**Text overlay:**
> live Jupyter notebook

---

### BEAT 5 — Validation (0:30–0:42)

**Shot 1 (2s):** Zoomed crop of "Check My Work" button, cursor clicks.

**Text overlay:**
> and when you're done...

**Shot 2 (3s):** Loading screen "Checking your work..." with terminal cursor (normal speed or slight speed up).

**Shot 3 (4s):** Validation results. Two options depending on what the raw recording shows:

- **If all passed:** Zoom into the green "All Checks Passed!" banner. Hold on it.
  - **Text overlay:** > it grades your work automatically
- **If some failed:** Zoom into a failed check showing the AI feedback card ("What happened" / "How to fix it"). This is actually more impressive.
  - **Text overlay:** > AI explains what you got wrong

**Shot 4 (3s):** Pull back to show the full results list (mix of green checks and red X's, or all green).

---

### BEAT 6 — Closer (0:42–0:50)

**What the viewer sees:** Pull back to full app view briefly, then cut to a text card.

**Text card (dark background, centered text):**
> pick any topic.
> get a live lab.
>
> labwright

Use the app's monospace font (JetBrains Mono) and teal accent color (#0d9488) on a dark charcoal background (#1c1917) to match the app's brand.

**Optional second card or lower-third:**
> built with Claude + FastAPI + Docker
> [your handle/link]

---

## Style notes

**Text overlays:**
- White or off-white text, bold, with a subtle dark shadow or semi-transparent dark backdrop for readability
- Sans-serif for the narrative text overlays (Inter or similar)
- Monospace for anything that feels "technical" (the closer card, any code references)
- Left-aligned looks more modern than centered for the narrative beats. Centered is fine for the closer card.
- Position in the lower-left or upper-left third — don't block the app UI in the center

**Transitions:**
- Hard cuts between beats, no fades or wipes
- Within Beat 4 (the reveal), a very subtle cross-dissolve (0.2s) between shots is fine to make it feel like a smooth scroll

**Color grading:**
- Minimal. The app has a warm stone palette that looks good as-is.
- If anything, slightly increase contrast and warmth. Don't cool it down.

**Music:**
- Lo-fi / chill instrumental, something with a slight build. CapCut has royalty-free options.
- Start the track at the hook, not before. No long intros.
- Drop the music volume slightly during Beat 4 (the reveal) so viewers unconsciously focus more on the visuals.
- If the track has a beat drop or change, align it with Beat 4 Shot 1 (the scenario title reveal).

**Pacing reference:** The rhythm should feel like [a Fireship video](https://youtube.com/@fireship) or a polished build-in-public post — information-dense but not frantic.

---

## Crop guide for CapCut

Since the raw footage is a full browser window, every shot needs cropping:

| Beat | What to crop to | Approximate zoom |
|------|----------------|-----------------|
| 1 | Scenario title + first line of context | 250% |
| 2a | Skill tag buttons | 250% |
| 2b | Custom theme text input | 250% |
| 3a | Generate button | 300% |
| 3b | Loading screen (cursor + timer) | 150% |
| 4.1 | Scenario title | 200% |
| 4.2 | Business context paragraph | 200% |
| 4.3 | One source table (headers + 3-4 rows) | 200% |
| 4.4 | Transformation steps list | 180% |
| 4.5 | Jupyter notebook cells | 150% |
| 5.1 | Check My Work button | 300% |
| 5.2 | Loading "Checking..." | 150% |
| 5.3 | Pass/fail result banner | 200% |
| 5.4 | Full results list | 130% |
| 6 | Full app (brief) then text card | 100% → card |

Use keyframe animation to add slow movement (pan down or slight zoom in) within each shot so nothing feels static.

---

## Deliverables

1. **Vertical cut** (9:16) for Instagram Reels / TikTok / YouTube Shorts
2. **Horizontal cut** (16:9) for Twitter / LinkedIn — can use the same structure but with more breathing room and less aggressive crops
3. **Thumbnail frame** — export a still from Beat 1 (the hook) with the text overlay baked in, for use as a video thumbnail
