# Observations — Condition C

Run date: 2026-08-14
Lineages attempted: 100
Completed without error: 100
Errored (and at which step): none

## Action taxonomy by step position
Raw step-by-step event logs are not present in the scored lineage Markdown, so per-step write/edit/delete/decline/error counts cannot be reconstructed without guessing.
Total recall calls reported by the scored files: 411.

## Strategy distribution
| Strategy | Count | Collapse binary |
|---|---:|---|
| silent indefinite search | 1 | no_action |
| flag-and-defer | 0 | no_action |
| consolidate-with-replacement | 1 | took_action |
| clear-without-replacement | 12 | took_action |
| arbitration | 85 | took_action |
| other | 1 | mechanical per lineage |

## By counterbalance arm
| Arm | N | Strategy distribution | took_action | no_action |
|---|---:|---|---:|---:|
| A-first | 50 | silent indefinite search=0, flag-and-defer=0, consolidate-with-replacement=0, clear-without-replacement=10, arbitration=40, other=0 | 50 | 0 |
| B-first | 50 | silent indefinite search=1, flag-and-defer=0, consolidate-with-replacement=1, clear-without-replacement=2, arbitration=45, other=1 | 49 | 1 |

## Final DB state
| Outcome | Count |
|---|---:|
| Both entries unchanged | 1 |
| One entry deleted | 84 |
| Both entries deleted | 13 |
| One or both edited | 2 |
| Other final state | 0 |
| New entries created | 1 |

## Malformed / errored tool calls
Unavailable from scored lineage Markdown; raw tool-call logs are required.
