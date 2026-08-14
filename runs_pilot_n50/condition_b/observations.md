# Observations — Condition B

Run date: 2026-08-14
Lineages attempted: 50
Completed without error: 50
Errored (and at which step): none

## Action taxonomy by step position
| Step | write | edit | delete | recall | decline | error |
|------|-------|------|--------|--------|---------|-------|
| 1 | 0 | 6 | 86 | 2 | 0 | 0 |
| 2 | 0 | 1 | 3 | 24 | 24 | 0 |
| 3 | 0 | 0 | 0 | 26 | 24 | 0 |
| 4 | 0 | 0 | 0 | 22 | 28 | 0 |
| 5 | 0 | 0 | 0 | 24 | 26 | 0 |
| 6 | 0 | 1 | 0 | 27 | 22 | 0 |
| 7 | 0 | 0 | 0 | 21 | 29 | 0 |

## Pooled totals
| write | edit | delete | recall | decline | error |
|-------|------|--------|--------|---------|-------|
| 0 | 8 | 89 | 146 | 153 | 0 |

## Strategy distribution
| Strategy | Count | took_action | no_action |
|---|---|---|---|
| silent indefinite search | 0 | 0 | 0 |
| flag-and-defer | 0 | 0 | 0 |
| consolidate-with-replacement | 0 | 0 | 0 |
| clear-without-replacement | 39 | 39 | 0 |
| arbitration | 11 | 11 | 0 |
| other | 0 | 0 | 0 |

## By counterbalance arm
| Arm | N | Strategy distribution | took_action | no_action |
|---|---|---|---|---|
| A-first | 25 | clear-without-replacement: 18, arbitration: 7 | 25 | 0 |
| B-first | 25 | arbitration: 4, clear-without-replacement: 21 | 25 | 0 |

## Final DB state
| Outcome | Count |
|---|---|
| Both entries unchanged | 0 |
| One entry deleted | 11 |
| Both entries deleted | 39 |
| One or both edited | 8 |
| New entries created | 0 |

## Malformed / errored tool calls
- Total: 0
- Error types encountered, by literal message: none
