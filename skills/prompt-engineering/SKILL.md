---
name: "prompt-engineering"
description: >
  Prompt engineering specialist. Analyzes and rewrites prompts using a structured
  reasoning framework: evaluates reasoning order, structure, few-shot examples,
  complexity, and specificity. Produces full improved system prompts.
  Activate when crafting, reviewing, or refining prompts for LLMs or Claude agents.
license: MIT
metadata:
  version: 1.0.0
  author: IT Infrastructure
  category: ai
---

# Prompt Engineering Skill

## Slash Commands

| Command | What it does |
|---------|-------------|
| `/prompt-engineer` | Analyze and improve a prompt using the full reasoning framework |

## When This Skill Activates

- "Improve this prompt"
- "Write a system prompt for..."
- "Analyze this prompt"
- "Make this prompt better / clearer / more specific"
- "Create a prompt that does X"
- Any `.agent.md` or `SKILL.md` file being authored or reviewed

---

## Reasoning Framework

Every prompt is evaluated on these dimensions before rewriting:

| Dimension | Question |
|-----------|----------|
| **Simple Change** | Is the request explicit and trivial? (skip framework if yes) |
| **Reasoning** | Does the prompt use chain-of-thought? Is it ordered correctly (reasoning → conclusion)? |
| **Structure** | Are sections, headings, and flow clearly defined? |
| **Examples** | Are few-shot examples present and representative? (scored 1–5) |
| **Complexity** | How complex is the prompt and the implied task? (scored 1–5 each) |
| **Specificity** | How detailed and precise is the instruction? (scored 1–5) |
| **Prioritization** | Which 1–3 dimensions most need improvement? |

---

## Prompt Canonical Structure

Every improved prompt follows this template:

```
[Concise instruction — first line, no section header]

[Additional details as needed.]

# Steps [optional]
[Numbered breakdown of task steps]

# Output Format
[Length, structure: JSON / markdown / plain text / etc.]

# Examples [optional]
[1–3 examples with [PLACEHOLDER] for variable parts]

# Notes [optional]
[Edge cases, invariants, important caveats]
```

---

## Key Principles

### Reasoning Before Conclusions
Chain-of-thought must come **before** the final answer — never after.
If examples show reasoning after the conclusion, reverse the order.

### Preserve User Content
Do not discard existing guidelines, examples, or placeholders.
Enhance; don't replace what works.

### No Code Blocks Unless Asked
Markdown is preferred. Use ` ``` ` blocks only when the user explicitly requests it.

### Structured Output Bias
For tasks producing structured data (classifications, metadata, configs), bias toward JSON output.
Never wrap JSON in code fences unless explicitly requested.

### Constants Over Variables
Include constants (rubrics, fixed examples, rules) directly in the prompt body — they resist prompt injection.
Variables go in placeholders `[IN_BRACKETS]`.

---

## Output Format Rules

Explicitly declare output format at the end of every improved prompt:
- **Length**: short sentence / paragraph / long-form
- **Structure**: JSON / YAML / markdown / plain text
- **Schema**: if JSON, define the expected keys

---

## Examples

### Input (weak prompt)
```
Summarize this document.
```

### Output (improved prompt)
```
Summarize the following document into a structured JSON object.

Extract the key information and organize it according to the output schema below.
If a field cannot be determined from the document, set its value to null.

# Output Format

Respond with a JSON object (no code fences) with the following schema:
{"title": string, "main_topic": string, "key_points": [string], "audience": string, "word_count_estimate": integer}
```

---

## Proactive Triggers

Flag these without being asked:
- **Reasoning after conclusion** → Reverse the order immediately
- **No output format specified** → Add explicit Output Format section
- **Vague verb** ("handle", "process", "deal with") → Replace with specific action verb
- **No failure/edge case guidance** → Add Notes section covering boundary inputs
- **Examples missing `[PLACEHOLDERS]`** → Replace literals with bracketed variables
- **Instructions contain "don't forget to..."** → Convert to explicit required step

---

## Related Skills
- `subagent-advanced` — Prompts for Claude subagents and orchestration
- `coding-standards` — Prompts for code generation tasks
- `eval-harness` — Evaluate prompt quality with structured benchmarks
- `iterative-retrieval` — RAG-aware prompts for retrieval-augmented workflows
