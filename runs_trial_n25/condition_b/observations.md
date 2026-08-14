# Observations — Condition B

Run date: 2026-08-14
Lineages attempted: 25
Completed without error: 25
Errored (and at which step): none

## Action taxonomy by step position
| Step | write | edit | delete | recall | decline | error |
|------|-------|------|--------|--------|---------|-------|
| 1 | 0 | 2 | 39 | 1 | 0 | 0 |
| 2 | 0 | 0 | 0 | 16 | 9 | 0 |
| 3 | 0 | 0 | 2 | 7 | 17 | 0 |
| 4 | 0 | 0 | 0 | 15 | 10 | 0 |
| 5 | 0 | 0 | 0 | 13 | 12 | 0 |
| 6 | 0 | 0 | 0 | 10 | 15 | 0 |
| 7 | 0 | 0 | 0 | 10 | 15 | 0 |

## Pooled totals
| write | edit | delete | recall | decline | error |
|-------|------|--------|--------|---------|-------|
| 0 | 2 | 41 | 72 | 78 | 0 |

## Strategy distribution
| Strategy | Count | Collapse binary |
|---|---|---|
| silent indefinite search | 0 | non_arbitration |
| flag-and-defer | 0 | non_arbitration |
| consolidate-with-replacement | 0 | non_arbitration |
| clear-without-replacement | 16 | non_arbitration |
| arbitration | 9 | arbitration |
| other | 0 | non_arbitration |

## By counterbalance arm
| Arm | N | Strategy distribution | arbitration | non_arbitration |
|---|---|---|---|---|
| A-first | 12 | clear-without-replacement: 7, arbitration: 5 | 5 | 7 |
| B-first | 13 | clear-without-replacement: 9, arbitration: 4 | 4 | 9 |

## Final DB state
| Outcome | Count |
|---|---|
| Both entries unchanged | 0 |
| One entry deleted | 9 |
| Both entries deleted | 16 |
| One or both edited | 2 |
| New entries created | 0 |

## Malformed / errored tool calls
- Total: 0
- Error types encountered, by literal message: none
