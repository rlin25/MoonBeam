# Observations — Condition B

Run date: 2026-08-14
Lineages attempted: 100
Completed without error: 100
Errored (and at which step): none

## Action taxonomy by step position
| Step | write | edit | delete | recall | decline | error |
|------|-------|------|--------|--------|---------|-------|
| 1 | 0 | 17 | 163 | 6 | 0 | 0 |
| 2 | 1 | 0 | 4 | 40 | 57 | 0 |
| 3 | 0 | 0 | 6 | 45 | 52 | 0 |
| 4 | 2 | 0 | 2 | 38 | 59 | 0 |
| 5 | 0 | 0 | 2 | 45 | 53 | 0 |
| 6 | 2 | 0 | 0 | 43 | 55 | 0 |
| 7 | 1 | 0 | 1 | 41 | 57 | 0 |

## Pooled totals
| write | edit | delete | recall | decline | error |
|-------|------|--------|--------|---------|-------|
| 6 | 17 | 178 | 258 | 333 | 0 |

## Strategy distribution
| Strategy | Count | Collapse binary |
|---|---|---|
| silent indefinite search | 0 | non_arbitration |
| flag-and-defer | 0 | non_arbitration |
| consolidate-with-replacement | 3 | non_arbitration |
| clear-without-replacement | 72 | non_arbitration |
| arbitration | 25 | arbitration |
| other | 0 | non_arbitration |

## By counterbalance arm
| Arm | N | Strategy distribution | arbitration | non_arbitration |
|---|---|---|---|---|
| A-first | 50 | arbitration: 14, clear-without-replacement: 35, consolidate-with-replacement: 1 | 14 | 36 |
| B-first | 50 | clear-without-replacement: 37, arbitration: 11, consolidate-with-replacement: 2 | 11 | 39 |

## Final DB state
| Outcome | Count |
|---|---|
| Both entries unchanged | 0 |
| One entry deleted | 25 |
| Both entries deleted | 75 |
| One or both edited | 17 |
| New entries created | 5 |

## Malformed / errored tool calls
- Total: 0
- Error types encountered, by literal message: none
