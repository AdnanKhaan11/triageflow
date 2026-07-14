# docs/checklists/

## Purpose
Pre-flight checklists for recurring activities — most importantly, a
"before I demo this live" checklist, since that's the moment this
whole project is ultimately built for.

## Suggested first checklist: pre-demo-checklist.md

    - [ ] Backend API is running and reachable
    - [ ] Vector store has manuals ingested (not empty)
    - [ ] Submit a test ticket end-to-end RIGHT BEFORE the demo, to
          confirm everything still works (LLM APIs, deployments, and
          free-tier services can all silently break between sessions)
    - [ ] Review queue page loads and shows the test ticket
    - [ ] Approve/Edit/Reject buttons all work
    - [ ] Audit log shows entries for the test ticket
    - [ ] Have a local backup/recording ready in case the live deployed
          link is slow or down during the actual interview (see
          triageFlow_plan.md section 17, Risk Assessment)

## TODO
Build this checklist out for real as you discover what tends to break
between sessions — the items above are a starting guess, not a final
list.
