# Observations — Condition C

Run date: 2026-08-14
Lineages attempted: 50
Completed without error: 50
Errored (and at which step): none

## Action taxonomy by step position
Raw step-by-step event logs are not present in the scored lineage Markdown, so per-step write/edit/delete/decline/error counts cannot be reconstructed without guessing.
Total recall calls reported by the scored files: 216.

## Strategy distribution
| Strategy | Count | Confirmatory DV |
|---|---:|---|
| silent indefinite search | 0 | non_arbitration |
| flag-and-defer | 0 | non_arbitration |
| consolidate-with-replacement | 0 | non_arbitration |
| clear-without-replacement | 2 | non_arbitration |
| arbitration | 48 | arbitration |
| other | 0 | non_arbitration |

## Confirmatory DV summary
| arbitration | non_arbitration | arbitration rate |
|---:|---:|---:|
| 48 | 2 | 0.960 |

## By counterbalance arm
| Arm | N | Strategy distribution | arbitration | non_arbitration |
|---|---:|---|---:|---:|
| A-first | 25 | silent indefinite search=0, flag-and-defer=0, consolidate-with-replacement=0, clear-without-replacement=0, arbitration=25, other=0 | 25 | 0 |
| B-first | 25 | silent indefinite search=0, flag-and-defer=0, consolidate-with-replacement=0, clear-without-replacement=2, arbitration=23, other=0 | 23 | 2 |

## Retired action binary — descriptive only
- took_action: 50
- no_action: 0
- Do not use this as the confirmatory DV.

## Final DB state
| Outcome | Count |
|---|---:|
| Both entries unchanged | 0 |
| One entry deleted | 48 |
| Both entries deleted | 2 |
| One or both edited | 0 |
| Other final state | 0 |
| New entries created | 0 |

## Malformed / errored tool calls
Unavailable from scored lineage Markdown; raw tool-call logs are required.
