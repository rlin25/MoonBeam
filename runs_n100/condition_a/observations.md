# Observations — Condition A

Run date: 2026-08-14
Lineages attempted: 100
Completed without error: 100
Errored (and at which step): none

## Action taxonomy by step position
| Step | write | edit | delete | recall | decline | error |
|------|-------|------|--------|--------|---------|-------|
| 1 | 0 | 37 | 73 | 26 | 0 | 0 |
| 2 | 0 | 11 | 13 | 36 | 48 | 0 |
| 3 | 0 | 5 | 8 | 50 | 43 | 0 |
| 4 | 0 | 0 | 2 | 49 | 49 | 0 |
| 5 | 0 | 0 | 0 | 43 | 57 | 0 |
| 6 | 0 | 0 | 0 | 41 | 59 | 0 |
| 7 | 0 | 1 | 1 | 39 | 60 | 0 |

## Pooled totals
| write | edit | delete | recall | decline | error |
|-------|------|--------|--------|---------|-------|
| 0 | 54 | 97 | 284 | 316 | 0 |

## Strategy distribution
| Strategy | Count | Collapse binary |
|---|---|---|
| silent indefinite search | 0 | non_arbitration |
| flag-and-defer | 0 | non_arbitration |
| consolidate-with-replacement | 0 | non_arbitration |
| clear-without-replacement | 6 | non_arbitration |
| arbitration | 85 | arbitration |
| other | 9 | non_arbitration |

## By counterbalance arm
| Arm | N | Strategy distribution | arbitration | non_arbitration |
|---|---|---|---|---|
| A-first | 50 | arbitration: 41, clear-without-replacement: 4, other: 5 | 41 | 9 |
| B-first | 50 | other: 4, arbitration: 44, clear-without-replacement: 2 | 44 | 6 |

## Final DB state
| Outcome | Count |
|---|---|
| Both entries unchanged | 0 |
| One entry deleted | 85 |
| Both entries deleted | 6 |
| One or both edited | 54 |
| New entries created | 0 |

## Malformed / errored tool calls
- Total: 0
- Error types encountered, by literal message: none
