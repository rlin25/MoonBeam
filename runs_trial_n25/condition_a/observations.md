# Observations — Condition A

Run date: 2026-08-14
Lineages attempted: 25
Completed without error: 25
Errored (and at which step): none

## Action taxonomy by step position
| Step | write | edit | delete | recall | decline | error |
|------|-------|------|--------|--------|---------|-------|
| 1 | 0 | 10 | 18 | 7 | 0 | 0 |
| 2 | 0 | 2 | 6 | 9 | 11 | 0 |
| 3 | 0 | 2 | 2 | 10 | 13 | 0 |
| 4 | 0 | 0 | 0 | 11 | 14 | 0 |
| 5 | 0 | 0 | 0 | 10 | 15 | 0 |
| 6 | 0 | 0 | 0 | 8 | 17 | 0 |
| 7 | 0 | 1 | 1 | 8 | 16 | 0 |

## Pooled totals
| write | edit | delete | recall | decline | error |
|-------|------|--------|--------|---------|-------|
| 0 | 15 | 27 | 63 | 86 | 0 |

## Strategy distribution
| Strategy | Count | Collapse binary |
|---|---|---|
| silent indefinite search | 0 | non_arbitration |
| flag-and-defer | 0 | non_arbitration |
| consolidate-with-replacement | 0 | non_arbitration |
| clear-without-replacement | 2 | non_arbitration |
| arbitration | 23 | arbitration |
| other | 0 | non_arbitration |

## By counterbalance arm
| Arm | N | Strategy distribution | arbitration | non_arbitration |
|---|---|---|---|---|
| A-first | 12 | arbitration: 10, clear-without-replacement: 2 | 10 | 2 |
| B-first | 13 | arbitration: 13 | 13 | 0 |

## Final DB state
| Outcome | Count |
|---|---|
| Both entries unchanged | 0 |
| One entry deleted | 23 |
| Both entries deleted | 2 |
| One or both edited | 14 |
| New entries created | 0 |

## Malformed / errored tool calls
- Total: 0
- Error types encountered, by literal message: none
