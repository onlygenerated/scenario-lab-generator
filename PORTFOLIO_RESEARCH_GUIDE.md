# Guide: Creating a Portfolio Research Reference Document

Reusable instructions for generating a research-backed reference document for any portfolio project. The output serves two audiences: portfolio website copy and chatbot background knowledge.

---

## Step 1: Define What Your Project Actually Does

Before touching research, write a plain-language inventory of your project's features. Be specific and honest — this prevents overclaiming later.

Format as a bulleted list covering:
- What the user controls (inputs, choices, configuration)
- What the system does in response (generation, processing, output)
- What tools/environments are involved (real databases, sandboxes, APIs)
- What feedback mechanisms exist (validation, scoring, diagnostics)
- What the scope limitations are (single-session, no persistence, individual use only)

**Why this matters:** Every research connection you make later must map to something on this list. If your project doesn't do it, you can't claim the research supports it.

---

## Step 2: Identify 4-8 Pedagogical or Design Themes

Look at your feature list and ask: "What learning science or UX research principle does this implement?"

Common themes for technical/educational projects:
- Interest and relevance (learner choice, domain personalization)
- Active learning (hands-on practice vs. passive consumption)
- Scenario-based or problem-based learning (realistic contexts)
- Personalization or contextualization (tailored content)
- Feedback timing and quality (immediate, diagnostic, formative)
- Adaptive difficulty (matching challenge to skill level)
- Authentic tools and environments (professional-grade, not toy)
- Collaboration and social learning (if applicable)
- Cognitive load management (scaffolding, chunking)

Pick only themes your project genuinely addresses. 4-8 is the sweet spot — fewer feels thin, more feels like padding.

---

## Step 3: Find 1-2 Landmark Studies Per Theme

For each theme, find peer-reviewed studies that are:
- **Frequently cited** (1000+ citations on Google Scholar is a good signal)
- **Meta-analyses or RCTs when possible** (stronger evidence than single small studies)
- **From recognized journals** (not predatory publishers)

Search strategy:
1. Google Scholar the theme name (e.g., "active learning STEM meta-analysis")
2. Look for the paper that other papers cite — the one that shows up in every literature review
3. Prefer studies published in major journals (PNAS, Science, Educational Psychologist, Review of Educational Research)

You want landmark studies because they are independently verifiable — anyone with Google Scholar can confirm they exist and say what you claim they say.

**Format each citation in APA style.** This signals rigor to technical visitors and makes the document easy for a chatbot to parse.

---

## Step 4: Write Each Research Entry

Each entry follows this structure:

```
### Author(s) (Year). Title. *Journal, Volume*(Issue), Pages.

2-3 sentence summary of findings. State the key result directly — no hedging.
Lead with what the study found, not what it "explored" or "investigated."

**[Project name] connection:** 1-2 sentences mapping the finding to a specific
feature in your project. Be concrete — name the feature, describe what the
user experiences.
```

Writing rules:
- **State findings directly.** "Active learning raised exam scores by 6%" not "Research suggests active learning may potentially improve outcomes."
- **No hedging language.** Cut "perhaps," "it could be argued," "some evidence suggests." The studies either found it or they didn't.
- **Be specific in connections.** "Learners write real SQL against real PostgreSQL" not "learners engage with authentic tools." Name the tool, name the action.
- **Don't overclaim.** If your project partially implements something, say so. "Labwright's difficulty selector controls complexity at generation time" — not "Labwright provides fully adaptive intelligent tutoring."

---

## Step 5: Write 1-2 Critical Notes

This is the section that builds credibility. Pick the 1-2 gaps that would most improve outcomes if addressed.

Good critical notes have three properties:
1. **Research-backed** — cite a study showing why this matters
2. **Specific** — name exactly what's missing and why it matters
3. **Forward-looking** — frame as "what I'd build next," not "what's wrong"

Structure:

```
### [Gap Name]

**Citation(s)** in APA format.

1-2 paragraphs explaining:
- What the research says
- Why your project doesn't fully address it (be honest about the constraint — time, scope, architecture)
- What you would build to close the gap

Frame the closing sentence as future work: "With more time, I would add..."
or "Future work would include..."
```

**How to choose which gaps:** Ask yourself, "If a hiring manager who knows learning science looked at my project, what would they notice is missing?" Address those before they ask.

Avoid:
- Vague hand-waving ("there's always room for improvement")
- Apologetic tone ("unfortunately, the project fails to...")
- Gaps that undermine your core thesis (pick gaps that extend the work, not gaps that invalidate it)

---

## Step 6: Write the Opening

Write this last, after you know what the document contains.

2-3 sentences covering:
1. What this document is (research reference for portfolio and chatbot use)
2. What the project does (one sentence)
3. The core claim (every design choice maps to established research)

Keep it short. The research sections do the heavy lifting.

---

## Step 7: Review Checklist

Before publishing:

- [ ] Every citation is a real, findable study (check Google Scholar)
- [ ] Every "connection" maps to a feature the project actually has
- [ ] No hedging language ("perhaps," "may potentially," "it could be argued")
- [ ] Critical notes are specific, research-backed, and forward-looking
- [ ] Critical notes don't undermine the core thesis
- [ ] Document reads well if someone extracts a single section (chatbot use case)
- [ ] No claims about features that don't exist or research that doesn't say what you claim
- [ ] APA citations are correctly formatted
- [ ] Tone is confident throughout — including the critical notes

---

## Template

```markdown
# Research Foundation

[2-3 sentence opening: what this document is, what the project does, core claim.]

---

## 1. [Theme Name]

### Author(s) (Year). Title. *Journal, Volume*(Issue), Pages.

[2-3 sentence summary of findings.]

**[Project] connection:** [1-2 sentences mapping finding to specific feature.]

### Author(s) (Year). Title. *Journal, Volume*(Issue), Pages.

[2-3 sentence summary of findings.]

**[Project] connection:** [1-2 sentences mapping finding to specific feature.]

---

[Repeat for each theme — aim for 4-8 sections, 1-2 studies each]

---

## Critical Notes: What I Would Build Next

### [Gap 1 Name]

**Citation(s)** in APA format.

[1-2 paragraphs: what the research says, why the project doesn't fully
address it, what you would build to close the gap.]

### [Gap 2 Name]

**Citation(s)** in APA format.

[1-2 paragraphs: same structure.]
```

---

## Example Prompt for AI-Assisted Generation

If using an AI assistant to help draft the document, provide:

1. The feature inventory from Step 1
2. The themes you identified in Step 2
3. Any studies you already know are relevant
4. The project name and one-sentence description
5. Known limitations or gaps you want to address honestly

Then ask for the document following this guide's structure and tone rules. Review every citation independently — AI can hallucinate study details, so verify titles, authors, years, and journals against Google Scholar before publishing.
