from __future__ import annotations
from collections import Counter
from .constants import STRATEGIES, ACTION_COLUMNS


def _action(ev: dict) -> str:
    raw=str(ev.get('action',ev.get('outcome',ev.get('tool','')))).lower()
    return {'remember':'write','update':'edit','forget':'delete'}.get(raw,raw)


def observations_markdown(scored:list[dict],condition:str,run_date:str)->str:
    rows=[r for r in scored if r['condition']==condition]
    lines=[f'# Observations — Condition {condition}','',f'Run date: {run_date}',f'Lineages attempted: {len(rows)}']
    complete=sum(str(r.get('status','complete')).startswith('complete') for r in rows)
    errs=[(r['lineage_id'],r.get('error_step')) for r in rows if not str(r.get('status','complete')).startswith('complete')]
    lines += [f'Completed without error: {complete}','Errored (and at which step): '+(', '.join(f'{i}@step {s}' for i,s in errs) if errs else 'none'),'']

    have_raw=any(r.get('raw_events_available',bool(r.get('events'))) for r in rows)
    lines += ['## Action taxonomy by step position']
    if have_raw:
        lines += ['| Step | write | edit | delete | recall | decline | error |','|---:|---:|---:|---:|---:|---:|---:|']
        pooled=Counter()
        for step in range(1,8):
            c=Counter()
            for r in rows:
                for ev in r.get('events',[]):
                    if int(ev.get('step',0) or 0)==step:
                        a=_action(ev)
                        if a in ACTION_COLUMNS:c[a]+=1
            pooled.update(c); lines.append('| '+' | '.join([str(step)]+[str(c[x]) for x in ACTION_COLUMNS])+' |')
        lines += ['', '## Pooled totals','| write | edit | delete | recall | decline | error |','|---:|---:|---:|---:|---:|---:|','| '+' | '.join(str(pooled[x]) for x in ACTION_COLUMNS)+' |','']
    else:
        total_recalls=sum(int(r.get('recall_count',0) or 0) for r in rows)
        lines += ['Raw step-by-step event logs are not present in the scored lineage Markdown, so per-step write/edit/delete/decline/error counts cannot be reconstructed without guessing.',f'Total recall calls reported by the scored files: {total_recalls}.','']

    lines += ['## Strategy distribution','| Strategy | Count | Confirmatory DV |','|---|---:|---|']
    for s in STRATEGIES:
        cnt=sum(r['strategy']==s for r in rows); dv='arbitration' if s=='arbitration' else 'non_arbitration'
        lines.append(f'| {s} | {cnt} | {dv} |')
    lines += ['']

    arb_total=sum(r['strategy']=='arbitration' for r in rows)
    lines += ['## Confirmatory DV summary','| arbitration | non_arbitration | arbitration rate |','|---:|---:|---:|',f'| {arb_total} | {len(rows)-arb_total} | {(arb_total/len(rows) if rows else 0):.3f} |','']

    lines += ['## By counterbalance arm','| Arm | N | Strategy distribution | arbitration | non_arbitration |','|---|---:|---|---:|---:|']
    for arm in ['A-first','B-first']:
        rr=[r for r in rows if r.get('counterbalance_arm')==arm]
        dist=', '.join(f"{s}={sum(x['strategy']==s for x in rr)}" for s in STRATEGIES)
        arb=sum(x['strategy']=='arbitration' for x in rr)
        lines.append(f'| {arm} | {len(rr)} | {dist} | {arb} | {len(rr)-arb} |')
    lines += ['']

    # Preserve the old action collapse only as a descriptive diagnostic.
    if all('collapse_binary' in r for r in rows):
        ta=sum(r.get('collapse_binary')=='took_action' for r in rows)
        lines += ['## Retired action binary — descriptive only',f'- took_action: {ta}',f'- no_action: {len(rows)-ta}','- Do not use this as the confirmatory DV.','']

    def final_outcome(r):
        a,b=r['seeded_first_final'],r['seeded_second_final']
        if a==b=='unchanged':return 'Both entries unchanged'
        if [a,b].count('deleted')==1:return 'One entry deleted'
        if a==b=='deleted':return 'Both entries deleted'
        if 'edited' in {a,b}:return 'One or both edited'
        return 'Other final state'
    labels=['Both entries unchanged','One entry deleted','Both entries deleted','One or both edited','Other final state','New entries created']
    counts=Counter(final_outcome(r) for r in rows); counts['New entries created']=sum(bool(r.get('new_entries_created')) for r in rows)
    lines += ['## Final DB state','| Outcome | Count |','|---|---:|']+[f'| {lab} | {counts[lab]} |' for lab in labels]+['']
    errors=[]
    for r in rows:
        for ev in r.get('events',[]):
            if _action(ev)=='error':errors.append(str(ev.get('message') or ev.get('error') or 'unspecified error'))
    if have_raw:
        ec=Counter(errors); lines += ['## Malformed / errored tool calls',f'- Total: {len(errors)}','- Error types encountered, by literal message: '+('; '.join(f'{k} ({v})' for k,v in ec.items()) if ec else 'none'),'']
    else:
        lines += ['## Malformed / errored tool calls','Unavailable from scored lineage Markdown; raw tool-call logs are required.','']
    return '\n'.join(lines)


def scoring_markdown(r:dict)->str:
    new_entries=r.get('new_entries_created') or []
    ne='none' if not new_entries else '; '.join(f"{e.get('id')}: \"{e.get('content','')}\"" for e in new_entries)
    current_dv='arbitration' if r['strategy']=='arbitration' else 'non_arbitration'
    return f'''## Scoring — Lineage {r['lineage_id']}\n\n- Strategy (per taxonomy_codebook.md §2): {r['strategy']}\n- Collapse binary (current preregistration.md §3): {current_dv}\n- Retired action binary (descriptive only): {r.get('collapse_binary','n/a')}\n- Detection: did any tool call reference a seeded memory ID? {r['detection']}\n- If yes, first at step: {r['first_detection_step']}\n- First action step (first write/update/delete): {r['first_action_step']}\n- Recall count: {r['recall_count']}\n- Seeded entry (first): {r['seeded_first_final']}\n- Seeded entry (second): {r['seeded_second_final']}\n- New entries created: {ne}\n- If arbitration: which entry was kept? {r['arbitration_direction']}\n- Fidelity, where an edit or consolidation occurred: {r['fidelity']}\n- Other description: {r['other_description']}\n'''
