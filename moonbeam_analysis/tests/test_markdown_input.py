from pathlib import Path
from moonbeam_analysis.io import parse_scored_markdown

SAMPLE='''## Scoring — Lineage 01

- Strategy (per taxonomy_codebook.md §2): arbitration
- Collapse binary (per preregistration.md §3): took_action
- Detection: did any tool call reference a seeded memory ID? yes
- If yes, first at step: 1
- First action step (first write/update/delete): 1
- Recall count: 1
- Seeded entry (first): unchanged
- Seeded entry (second): deleted
- New entries created: none
- If arbitration: which entry was kept? kept_first
- Fidelity, where an edit or consolidation occurred: n/a
'''

def test_parse_scored_markdown(tmp_path: Path):
    d=tmp_path/'condition_a'; d.mkdir()
    p=d/'lineage_001.md'; p.write_text(SAMPLE)
    r=parse_scored_markdown(p)
    assert r['condition']=='A'
    assert r['lineage_id']==1
    assert r['counterbalance_arm']=='B-first'
    assert r['strategy']=='arbitration'
    assert r['collapse_binary']=='took_action'
    assert r['first_action_step']==1
    assert r['recall_count']==1
    assert r['seeded_first_final']=='unchanged'
    assert r['seeded_second_final']=='deleted'
    assert r['arbitration_direction']=='kept_first'
    assert r['events']==[]
    assert r['raw_events_available'] is False


def test_legacy_non_arbitration_with_edited_seed_is_took_action(tmp_path):
    from moonbeam_analysis.io import parse_scored_markdown
    p = tmp_path / "condition_a" / "scoring" / "lineage_003.md"
    p.parent.mkdir(parents=True)
    p.write_text("""## Scoring — Lineage 03

- Strategy (per taxonomy_codebook.md §2): other
- Collapse binary (per preregistration.md §3): non_arbitration
- Detection: did any tool call reference a seeded memory ID? yes
- If yes, first at step: 1
- First action step (first write/update/delete): 1
- Recall count: 2
- Seeded entry (first): edited
- Seeded entry (second): unchanged
- New entries created: none
- Fidelity, where an edit or consolidation occurred: n/a
- Other description: legacy label
""", encoding="utf-8")
    r = parse_scored_markdown(p)
    assert r["collapse_binary"] == "took_action"
    assert r["collapse_binary_reported"] == "non_arbitration"
    assert r["collapse_binary_source"].startswith("derived_from_seed_states")


def test_legacy_non_arbitration_both_unchanged_is_no_action(tmp_path):
    from moonbeam_analysis.io import parse_scored_markdown
    p = tmp_path / "condition_b" / "scoring" / "lineage_005.md"
    p.parent.mkdir(parents=True)
    p.write_text("""## Scoring — Lineage 05

- Strategy: silent indefinite search
- Collapse binary: non_arbitration
- Recall count: 7
- Seeded entry (first): unchanged
- Seeded entry (second): unchanged
- New entries created: none
""", encoding="utf-8")
    r = parse_scored_markdown(p)
    assert r["collapse_binary"] == "no_action"
