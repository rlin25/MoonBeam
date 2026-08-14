# Observations — Condition A

Run date: 2026-08-14
Lineages attempted: 50
Completed without error: 50
Errored (and at which step): none

## Action taxonomy by step position
| Step | write | edit | delete | recall | decline | error |
|------|-------|------|--------|--------|---------|-------|
| 1 | 0 | 15 | 46 | 8 | 0 | 0 |
| 2 | 0 | 3 | 5 | 19 | 26 | 0 |
| 3 | 0 | 0 | 0 | 19 | 31 | 0 |
| 4 | 0 | 0 | 0 | 24 | 26 | 0 |
| 5 | 0 | 1 | 2 | 17 | 31 | 0 |
| 6 | 0 | 0 | 0 | 21 | 29 | 0 |
| 7 | 0 | 0 | 0 | 19 | 31 | 0 |

## Pooled totals
| write | edit | delete | recall | decline | error |
|-------|------|--------|--------|---------|-------|
| 0 | 19 | 53 | 127 | 174 | 0 |

## Strategy distribution
| Strategy | Count | took_action | no_action |
|---|---|---|---|
| silent indefinite search | 1 | 0 | 1 |
| flag-and-defer | 0 | 0 | 0 |
| consolidate-with-replacement | 0 | 0 | 0 |
| clear-without-replacement | 5 | 5 | 0 |
| arbitration | 43 | 43 | 0 |
| other | 1 | 1 | 0 |

## By counterbalance arm
| Arm | N | Strategy distribution | took_action | no_action |
|---|---|---|---|---|
| A-first | 25 | arbitration: 23, clear-without-replacement: 2 | 25 | 0 |
| B-first | 25 | arbitration: 20, other: 1, clear-without-replacement: 3, silent indefinite search: 1 | 24 | 1 |

## Final DB state
| Outcome | Count |
|---|---|
| Both entries unchanged | 1 |
| One entry deleted | 43 |
| Both entries deleted | 5 |
| One or both edited | 19 |
| New entries created | 0 |

## Malformed / errored tool calls
- Total: 0
- Error types encountered, by literal message: none
