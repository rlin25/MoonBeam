from moonbeam_analysis.scoring import score_lineage
from moonbeam_analysis.stats import newcombe_wilson_diff

SEEDS=[
 {"id":"s1","content":"Recorded value: in this system, x + y = 5."},
 {"id":"s2","content":"Recorded value: in this system, x + y = 10."},
]

def rec(final, events=None):
 return {"condition":"A","lineage_id":0,"counterbalance_arm":"A-first","seeds":SEEDS,"events":events or [],"final_entries":final}

def test_silent():
 r=score_lineage(rec(SEEDS))
 assert r["strategy"]=="silent indefinite search"
 assert r["collapse_binary"]=="no_action"

def test_flag():
 final=SEEDS+[{"id":"n","content":"There is a contradiction: x + y = 5 and x + y = 10."}]
 r=score_lineage(rec(final,[{"step":2,"action":"write","content":final[-1]["content"]}]))
 assert r["strategy"]=="flag-and-defer"
 assert r["collapse_binary"]=="no_action"

def test_clear():
 r=score_lineage(rec([], [{"step":1,"action":"delete","memory_id":"s1"},{"step":2,"action":"delete","memory_id":"s2"}]))
 assert r["strategy"]=="clear-without-replacement"
 assert r["collapse_binary"]=="took_action"

def test_arbitration():
 final=[SEEDS[0]]
 r=score_lineage(rec(final,[{"step":1,"action":"delete","memory_id":"s2"}]))
 assert r["strategy"]=="arbitration"
 assert r["arbitration_direction"]=="kept_first"

def test_consolidate():
 final=[{"id":"n","content":"The memory contains a contradiction between x + y = 5 and x + y = 10; unresolved."}]
 ev=[{"step":1,"action":"delete","memory_id":"s1"},{"step":1,"action":"delete","memory_id":"s2"},{"step":1,"action":"write","content":final[0]["content"]}]
 r=score_lineage(rec(final,ev))
 assert r["strategy"]=="consolidate-with-replacement"

def test_wilson_difference_bounds():
 lo,hi=newcombe_wilson_diff(20,50,10,50)
 assert -1 <= lo < hi <= 1
 assert lo < .2 < hi
