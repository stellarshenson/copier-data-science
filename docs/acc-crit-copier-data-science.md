# Acceptance criteria - copier-data-science

What the template must do for a project generated from it to be usable. One item per criterion, each closed only against evidence that it holds.

## Authors

- `@kj` Konrad Jelen

## Template options `OPTS`

the questions copier.yml asks and the values they accept

- [ ] `ACC-OPTS-1` **the AI assistant question takes more than one assistant** - MEDIUM; `ai_assistant` is a single choice, so a project carrying instructions for Claude and for Gemini can declare only one of them; it becomes a multiselect, every template condition reading it tests for membership rather than equality, the rendered project gets one instructions file and one internal resources folder per assistant chosen, and choosing none stays possible; `copier.yml`
  - test: run the survey, tick claude and gemini together, render, and check both instruction files and both resource folders are present
  - test-tags: FUNCTIONAL
  - log: 2026-08-29T19:12:44Z @kj added

