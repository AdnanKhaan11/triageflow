# Drafting Agent — Implementation Notes

## Responsibilities
- Synthesize classification + retrieved manual content + inventory
  check into a single, human-readable recommendation.
- Ground the recommendation in retrieved content, with citations.

## Inputs
- Classification dict, retrieved_chunks list, inventory_check dict.

## Outputs
- A draft recommendation (text, ideally lightly structured), citing
  its sources.

## Suggested Approach
1. Design a prompt that explicitly instructs the model to use ONLY
   the provided manual excerpts for factual procedure claims.
2. Decide on an output format (plain text vs. light structure like
   Diagnosis/Action/Parts/Escalation sections).
3. Explicitly handle the empty-retrieval case — the draft should
   say 'no matching procedure found' rather than inventing one.

## Common Mistakes
- Allowing confident-sounding hallucinated recommendations when
  retrieval came back empty or weak.
- Omitting source citations, which undermines the project's
  'auditable recommendation' thesis.

## Debugging Tips
- Log the FULL assembled prompt during development — prompt
  template bugs that silently drop an input are easy to miss from
  the output text alone.

## Learning Objectives
- Understand prompt-grounding techniques to reduce hallucination.
- Understand why explainability/citation matters for AI systems
  used in safety-relevant decisions.

---
*This is a guidance document only. No implementation code lives here —
see the corresponding source file's docstring for the actual TODO list.*
