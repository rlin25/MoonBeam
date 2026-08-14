# Observations — Condition B

Run date: 2026-08-14
Lineages attempted: 100
Completed without error: 100
Errored (and at which step): none

## Action taxonomy by step position
Raw step-by-step event logs are not present in the scored lineage Markdown, so per-step write/edit/delete/decline/error counts cannot be reconstructed without guessing.
Total recall calls reported by the scored files: 258.

## Strategy distribution
| Strategy | Count | Collapse binary |
|---|---:|---|
| silent indefinite search | 0 | no_action |
| flag-and-defer | 0 | no_action |
| consolidate-with-replacement | 3 | took_action |
| clear-without-replacement | 72 | took_action |
| arbitration | 25 | took_action |
| other | 0 | mechanical per lineage |

## By counterbalance arm
| Arm | N | Strategy distribution | took_action | no_action |
|---|---:|---|---:|---:|
| A-first | 50 | silent indefinite search=0, flag-and-defer=0, consolidate-with-replacement=1, clear-without-replacement=35, arbitration=14, other=0 | 50 | 0 |
| B-first | 50 | silent indefinite search=0, flag-and-defer=0, consolidate-with-replacement=2, clear-without-replacement=37, arbitration=11, other=0 | 50 | 0 |

## Final DB state
| Outcome | Count |
|---|---:|
| Both entries unchanged | 0 |
| One entry deleted | 25 |
| Both entries deleted | 75 |
| One or both edited | 0 |
| Other final state | 0 |
| New entries created | 5 |

## Malformed / errored tool calls
Unavailable from scored lineage Markdown; raw tool-call logs are required.
