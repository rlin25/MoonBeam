# Observations — Condition C

Run date: 2026-08-14
Lineages attempted: 25
Completed without error: 25
Errored (and at which step): none

## Action taxonomy by step position
| Step | write | edit | delete | recall | decline | error |
|------|-------|------|--------|--------|---------|-------|
| 1 | 0 | 15 | 15 | 9 | 0 | 0 |
| 2 | 0 | 6 | 6 | 13 | 6 | 0 |
| 3 | 0 | 1 | 3 | 10 | 13 | 0 |
| 4 | 0 | 2 | 0 | 14 | 10 | 0 |
| 5 | 1 | 1 | 1 | 16 | 7 | 0 |
| 6 | 0 | 0 | 0 | 17 | 8 | 0 |
| 7 | 0 | 0 | 0 | 14 | 11 | 0 |

## Pooled totals
| write | edit | delete | recall | decline | error |
|-------|------|--------|--------|---------|-------|
| 1 | 25 | 25 | 93 | 55 | 0 |

## Strategy distribution
| Strategy | Count | Collapse binary |
|---|---|---|
| silent indefinite search | 1 | non_arbitration |
| flag-and-defer | 0 | non_arbitration |
| consolidate-with-replacement | 1 | non_arbitration |
| clear-without-replacement | 1 | non_arbitration |
| arbitration | 21 | arbitration |
| other | 1 | non_arbitration |

## By counterbalance arm
| Arm | N | Strategy distribution | arbitration | non_arbitration |
|---|---|---|---|---|
| A-first | 12 | arbitration: 10, consolidate-with-replacement: 1, clear-without-replacement: 1 | 10 | 2 |
| B-first | 13 | arbitration: 11, other: 1, silent indefinite search: 1 | 11 | 2 |

## Final DB state
| Outcome | Count |
|---|---|
| Both entries unchanged | 1 |
| One entry deleted | 21 |
| Both entries deleted | 2 |
| One or both edited | 21 |
| New entries created | 1 |

## Malformed / errored tool calls
- Total: 0
- Error types encountered, by literal message: none
