# Observations — Condition B

Run date: 2026-08-14
Lineages attempted: 100
Completed without error: 100
Errored (and at which step): none

## Action taxonomy by step position
Raw step-by-step event logs are not present in the scored lineage Markdown, so per-step write/edit/delete/decline/error counts cannot be reconstructed without guessing.
Total recall calls reported by the scored files: 258.

## Strategy distribution
| Strategy | Count | Confirmatory DV |
|---|---:|---|
| silent indefinite search | 0 | non_arbitration |
| flag-and-defer | 0 | non_arbitration |
| consolidate-with-replacement | 3 | non_arbitration |
| clear-without-replacement | 72 | non_arbitration |
| arbitration | 25 | arbitration |
| other | 0 | non_arbitration |

## Confirmatory DV summary
| arbitration | non_arbitration | arbitration rate |
|---:|---:|---:|
| 25 | 75 | 0.250 |

## By counterbalance arm
| Arm | N | Strategy distribution | arbitration | non_arbitration |
|---|---:|---|---:|---:|
| A-first | 50 | silent indefinite search=0, flag-and-defer=0, consolidate-with-replacement=1, clear-without-replacement=35, arbitration=14, other=0 | 14 | 36 |
| B-first | 50 | silent indefinite search=0, flag-and-defer=0, consolidate-with-replacement=2, clear-without-replacement=37, arbitration=11, other=0 | 11 | 39 |

## Retired action binary — descriptive only
- took_action: 100
- no_action: 0
- Do not use this as the confirmatory DV.

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
