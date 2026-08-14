# Observations — Condition C

Run date: 2026-08-14
Lineages attempted: 100
Completed without error: 100
Errored (and at which step): none

## Action taxonomy by step position
| Step | write | edit | delete | recall | decline | error |
|------|-------|------|--------|--------|---------|-------|
| 1 | 0 | 56 | 69 | 34 | 0 | 0 |
| 2 | 0 | 15 | 18 | 61 | 22 | 0 |
| 3 | 0 | 9 | 12 | 63 | 26 | 0 |
| 4 | 0 | 4 | 6 | 66 | 29 | 0 |
| 5 | 0 | 0 | 3 | 63 | 35 | 0 |
| 6 | 1 | 2 | 2 | 61 | 36 | 0 |
| 7 | 0 | 0 | 0 | 63 | 37 | 0 |

## Pooled totals
| write | edit | delete | recall | decline | error |
|-------|------|--------|--------|---------|-------|
| 1 | 86 | 110 | 411 | 185 | 0 |

## Strategy distribution
| Strategy | Count | Collapse binary |
|---|---|---|
| silent indefinite search | 1 | non_arbitration |
| flag-and-defer | 0 | non_arbitration |
| consolidate-with-replacement | 1 | non_arbitration |
| clear-without-replacement | 12 | non_arbitration |
| arbitration | 85 | arbitration |
| other | 1 | non_arbitration |

## By counterbalance arm
| Arm | N | Strategy distribution | arbitration | non_arbitration |
|---|---|---|---|---|
| A-first | 50 | clear-without-replacement: 10, arbitration: 40 | 40 | 10 |
| B-first | 50 | arbitration: 45, clear-without-replacement: 2, other: 1, consolidate-with-replacement: 1, silent indefinite search: 1 | 45 | 5 |

## Final DB state
| Outcome | Count |
|---|---|
| Both entries unchanged | 1 |
| One entry deleted | 84 |
| Both entries deleted | 13 |
| One or both edited | 78 |
| New entries created | 1 |

## Malformed / errored tool calls
- Total: 0
- Error types encountered, by literal message: none
