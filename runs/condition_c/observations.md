# Observations — Condition C

Run date: 2026-08-14
Lineages attempted: 50
Completed without error: 50
Errored (and at which step): none

## Action taxonomy by step position
| Step | write | edit | delete | recall | decline | error |
|------|-------|------|--------|--------|---------|-------|
| 1 | 0 | 36 | 34 | 15 | 0 | 0 |
| 2 | 0 | 10 | 9 | 29 | 11 | 0 |
| 3 | 0 | 4 | 4 | 35 | 11 | 0 |
| 4 | 0 | 2 | 3 | 32 | 15 | 0 |
| 5 | 0 | 1 | 0 | 34 | 15 | 0 |
| 6 | 0 | 1 | 1 | 38 | 11 | 0 |
| 7 | 0 | 1 | 1 | 33 | 16 | 0 |

## Pooled totals
| write | edit | delete | recall | decline | error |
|-------|------|--------|--------|---------|-------|
| 0 | 55 | 52 | 216 | 79 | 0 |

## Strategy distribution
| Strategy | Count | took_action | no_action |
|---|---|---|---|
| silent indefinite search | 0 | 0 | 0 |
| flag-and-defer | 0 | 0 | 0 |
| consolidate-with-replacement | 0 | 0 | 0 |
| clear-without-replacement | 2 | 2 | 0 |
| arbitration | 48 | 48 | 0 |
| other | 0 | 0 | 0 |

## By counterbalance arm
| Arm | N | Strategy distribution | took_action | no_action |
|---|---|---|---|---|
| A-first | 25 | arbitration: 25 | 25 | 0 |
| B-first | 25 | arbitration: 23, clear-without-replacement: 2 | 25 | 0 |

## Final DB state
| Outcome | Count |
|---|---|
| Both entries unchanged | 0 |
| One entry deleted | 48 |
| Both entries deleted | 2 |
| One or both edited | 48 |
| New entries created | 0 |

## Malformed / errored tool calls
- Total: 0
- Error types encountered, by literal message: none
