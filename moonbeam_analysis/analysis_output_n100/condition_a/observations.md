# Observations — Condition A

Run date: 2026-08-14
Lineages attempted: 100
Completed without error: 100
Errored (and at which step): none

## Action taxonomy by step position
Raw step-by-step event logs are not present in the scored lineage Markdown, so per-step write/edit/delete/decline/error counts cannot be reconstructed without guessing.
Total recall calls reported by the scored files: 284.

## Strategy distribution
| Strategy | Count | Confirmatory DV |
|---|---:|---|
| silent indefinite search | 0 | non_arbitration |
| flag-and-defer | 0 | non_arbitration |
| consolidate-with-replacement | 0 | non_arbitration |
| clear-without-replacement | 6 | non_arbitration |
| arbitration | 85 | arbitration |
| other | 9 | non_arbitration |

## Confirmatory DV summary
| arbitration | non_arbitration | arbitration rate |
|---:|---:|---:|
| 85 | 15 | 0.850 |

## By counterbalance arm
| Arm | N | Strategy distribution | arbitration | non_arbitration |
|---|---:|---|---:|---:|
| A-first | 50 | silent indefinite search=0, flag-and-defer=0, consolidate-with-replacement=0, clear-without-replacement=4, arbitration=41, other=5 | 41 | 9 |
| B-first | 50 | silent indefinite search=0, flag-and-defer=0, consolidate-with-replacement=0, clear-without-replacement=2, arbitration=44, other=4 | 44 | 6 |

## Retired action binary — descriptive only
- took_action: 100
- no_action: 0
- Do not use this as the confirmatory DV.

## Final DB state
| Outcome | Count |
|---|---:|
| Both entries unchanged | 0 |
| One entry deleted | 85 |
| Both entries deleted | 6 |
| One or both edited | 9 |
| Other final state | 0 |
| New entries created | 0 |

## Malformed / errored tool calls
Unavailable from scored lineage Markdown; raw tool-call logs are required.
