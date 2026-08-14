# Observations — Condition C

Run date: 2026-08-14
Lineages attempted: 25
Completed without error: 25
Errored (and at which step): none

## Action taxonomy by step position
Raw step-by-step event logs are not present in the scored lineage Markdown, so per-step write/edit/delete/decline/error counts cannot be reconstructed without guessing.
Total recall calls reported by the scored files: 93.

## Strategy distribution
| Strategy | Count | Collapse binary |
|---|---:|---|
| silent indefinite search | 1 | no_action |
| flag-and-defer | 0 | no_action |
| consolidate-with-replacement | 1 | took_action |
| clear-without-replacement | 1 | took_action |
| arbitration | 21 | took_action |
| other | 1 | mechanical per lineage |

## By counterbalance arm
| Arm | N | Strategy distribution | took_action | no_action |
|---|---:|---|---:|---:|
| A-first | 12 | silent indefinite search=0, flag-and-defer=0, consolidate-with-replacement=1, clear-without-replacement=1, arbitration=10, other=0 | 12 | 0 |
| B-first | 13 | silent indefinite search=1, flag-and-defer=0, consolidate-with-replacement=0, clear-without-replacement=0, arbitration=11, other=1 | 12 | 1 |

## Final DB state
| Outcome | Count |
|---|---:|
| Both entries unchanged | 1 |
| One entry deleted | 21 |
| Both entries deleted | 2 |
| One or both edited | 1 |
| Other final state | 0 |
| New entries created | 1 |

## Malformed / errored tool calls
Unavailable from scored lineage Markdown; raw tool-call logs are required.
