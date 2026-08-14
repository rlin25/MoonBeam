from pathlib import Path
import pandas as pd
from moonbeam_analysis.charts import generate_charts


def test_generate_paper_charts(tmp_path: Path):
    rows=[]
    for cond in ["A","B","C"]:
        for i in range(1,11):
            rows.append({
                "condition":cond,
                "lineage_id":i,
                "collapse_binary":"no_action" if cond=="A" and i==1 else "took_action",
                "strategy":"arbitration" if i <= 6 else "clear-without-replacement",
                "first_action_step":None if cond=="A" and i==1 else (i%3)+1,
                "recall_count":i%5,
                "counterbalance_arm":"A-first" if i%2==0 else "B-first",
                "seeded_first_final":"unchanged" if i%2 else "edited",
                "seeded_second_final":"deleted" if i<=6 else "edited",
                "arbitration_direction":"kept_first" if i<=4 else "kept_second",
            })
    df=pd.DataFrame(rows)
    status=generate_charts(df,tmp_path)
    assert (tmp_path/"README.md").exists()
    assert (tmp_path/"01_action_rate_with_ci.png").exists()
    assert (tmp_path/"02_effect_size_forest.png").exists()
    assert (tmp_path/"03_strategy_composition.png").exists()
    assert (tmp_path/"04_cumulative_first_action.png").exists()
    assert (tmp_path/"05_recall_distribution.png").exists()
    assert (tmp_path/"06_counterbalance_robustness.png").exists()
    text=(tmp_path/"README.md").read_text()
    assert "what each figure is telling you" in text
    assert "B − A" in text
    assert all(v=="generated" for v in status.values())
