#!/usr/bin/env python3
"""
반복 사용 효과 - 모든 항목별 완전 분석 표
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

목적: 표Ⅴ-7 완전판 생성
  - A1, A2, A3, B1, B2, B3, C1, C2, Total
  - 각 항목별 첫/마지막 세션 비교
  - Agent vs Freepass
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════
# 1. 데이터 로드
# ═══════════════════════════════════════════════════════════════════════════

BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / 'data' / 'llm_evaluations'
OUTPUT_DIR = BASE_DIR / 'scripts' / 'verification'

print("=" * 80)
print("📊 반복 사용 효과 - 전체 항목별 분석")
print("=" * 80)

df = pd.read_csv(DATA_DIR / 'llm_284sessions_complete.csv')

# 항목 정의
items = {
    'A1': 'avg_A1',
    'A2': 'avg_A2', 
    'A3': 'avg_A3',
    'B1': 'avg_B1',
    'B2': 'avg_B2',
    'B3': 'avg_B3',
    'C1': 'avg_C1',
    'C2': 'avg_C2'
}

# Total 계산
df['Total'] = df[list(items.values())].sum(axis=1)
items['Total'] = 'Total'

# 시간순 정렬
df = df.sort_values(['student_name', 'session_id'])

# 복수 세션 학생
student_sessions = df.groupby('student_name').agg({
    'session_id': 'count',
    'assigned_mode': 'first'
}).rename(columns={'session_id': 'n_sessions'})

multi_session_students = student_sessions[student_sessions['n_sessions'] >= 2]

print(f"\n✓ 복수 세션 학생: {len(multi_session_students)}명")
print(f"  Agent: {(multi_session_students['assigned_mode'] == 'agent').sum()}명")
print(f"  Freepass: {(multi_session_students['assigned_mode'] == 'freepass').sum()}명")

# ═══════════════════════════════════════════════════════════════════════════
# 2. 모든 항목별 첫/마지막 비교
# ═══════════════════════════════════════════════════════════════════════════

results = []

for item_name, col_name in items.items():
    print(f"\n분석 중: {item_name}...")
    
    for mode in ['agent', 'freepass']:
        mode_students = multi_session_students[multi_session_students['assigned_mode'] == mode].index
        
        first_scores = []
        last_scores = []
        
        for student in mode_students:
            student_data = df[df['student_name'] == student].sort_values('session_id')
            
            if len(student_data) >= 2:
                first_scores.append(student_data.iloc[0][col_name])
                last_scores.append(student_data.iloc[-1][col_name])
        
        if len(first_scores) > 0:
            first_scores = np.array(first_scores)
            last_scores = np.array(last_scores)
            
            # Paired t-test
            t_stat, p_val = stats.ttest_rel(first_scores, last_scores)
            
            first_mean = first_scores.mean()
            last_mean = last_scores.mean()
            change = last_mean - first_mean
            
            results.append({
                'item': item_name,
                'mode': mode.capitalize(),
                'n': len(first_scores),
                'first': round(first_mean, 2),
                'last': round(last_mean, 2),
                'change': round(change, 2),
                't': round(t_stat, 2),
                'p': round(p_val, 3)
            })

df_results = pd.DataFrame(results)

# ═══════════════════════════════════════════════════════════════════════════
# 3. 표 형식 변환 (논문용)
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("📋 논문용 표 생성")
print("=" * 80)

# Agent와 Freepass를 한 행에
table_rows = []

for item_name in items.keys():
    agent_data = df_results[(df_results['item'] == item_name) & (df_results['mode'] == 'Agent')].iloc[0]
    free_data = df_results[(df_results['item'] == item_name) & (df_results['mode'] == 'Freepass')].iloc[0]
    
    table_rows.append({
        '항목': item_name,
        'Agent_첫': agent_data['first'],
        'Agent_마지막': agent_data['last'],
        'Agent_변화': agent_data['change'],
        'Agent_p': agent_data['p'],
        'Free_첫': free_data['first'],
        'Free_마지막': free_data['last'],
        'Free_변화': free_data['change'],
        'Free_p': free_data['p']
    })

df_table = pd.DataFrame(table_rows)

# 유의성 표시
df_table['Agent_sig'] = df_table['Agent_p'].apply(lambda x: '**' if x < 0.01 else '*' if x < 0.05 else '')
df_table['Free_sig'] = df_table['Free_p'].apply(lambda x: '**' if x < 0.01 else '*' if x < 0.05 else '')

print("\n" + df_table.to_string(index=False))

# ═══════════════════════════════════════════════════════════════════════════
# 4. 마크다운 표 생성
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("📝 마크다운 표 생성")
print("=" * 80)

markdown_lines = []
markdown_lines.append("**[표Ⅴ-7] 세션 증가에 따른 항목별 점수 변화 (LLM 평가)**")
markdown_lines.append("")
markdown_lines.append("| 항목 | Agent 첫 | Agent 마지막 | Agent 변화 | Agent p | Freepass 첫 | Freepass 마지막 | Freepass 변화 | Freepass p |")
markdown_lines.append("|:----:|:--------:|:------------:|:----------:|:-------:|:-----------:|:---------------:|:-------------:|:----------:|")

for _, row in df_table.iterrows():
    item = row['항목']
    
    # Agent
    agent_first = f"{row['Agent_첫']:.2f}"
    agent_last = f"{row['Agent_마지막']:.2f}"
    agent_change = f"{row['Agent_변화']:+.2f}"
    agent_p = f"{row['Agent_p']:.3f}"
    
    # Freepass
    free_first = f"{row['Free_첫']:.2f}"
    free_last = f"{row['Free_마지막']:.2f}"
    free_change = f"{row['Free_변화']:+.2f}"
    free_p = f"{row['Free_p']:.3f}"
    
    # 유의성 표시
    if row['Agent_p'] < 0.01:
        agent_change = f"**{agent_change}**"
        agent_p = f"**{agent_p}**"
    elif row['Agent_p'] < 0.05:
        agent_change = f"**{agent_change}**"
        agent_p = f"**{agent_p}***"
    
    if row['Free_p'] < 0.01:
        free_change = f"**{free_change}**"
        free_p = f"**{free_p}**"
    elif row['Free_p'] < 0.05:
        free_change = f"**{free_change}**"
        free_p = f"**{free_p}***"
    
    # Total 행은 굵게
    if item == 'Total':
        markdown_lines.append(f"| **{item}** | **{agent_first}** | **{agent_last}** | {agent_change} | {agent_p} | **{free_first}** | **{free_last}** | {free_change} | {free_p} |")
    else:
        markdown_lines.append(f"| {item} | {agent_first} | {agent_last} | {agent_change} | {agent_p} | {free_first} | {free_last} | {free_change} | {free_p} |")

markdown_lines.append("")
markdown_lines.append("주: 복수 세션 참여 학생 (Agent n=23, Freepass n=27), paired t-test, *p<0.05, **p<0.01")

markdown_text = "\n".join(markdown_lines)

print(markdown_text)

# ═══════════════════════════════════════════════════════════════════════════
# 5. 저장
# ═══════════════════════════════════════════════════════════════════════════

# CSV 저장
df_results.to_csv(OUTPUT_DIR / 'TABLE_V7_ALL_ITEMS.csv', index=False, encoding='utf-8-sig')
df_table.to_csv(OUTPUT_DIR / 'TABLE_V7_FORMATTED.csv', index=False, encoding='utf-8-sig')

# 마크다운 저장
with open(OUTPUT_DIR / 'TABLE_V7_MARKDOWN.md', 'w', encoding='utf-8') as f:
    f.write(markdown_text)

print("\n" + "=" * 80)
print("✅ 저장 완료!")
print("=" * 80)
print(f"  - TABLE_V7_ALL_ITEMS.csv (원본 데이터)")
print(f"  - TABLE_V7_FORMATTED.csv (정리된 표)")
print(f"  - TABLE_V7_MARKDOWN.md (논문용 마크다운)")

# ═══════════════════════════════════════════════════════════════════════════
# 6. 유의한 항목 요약
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("📊 유의한 항목 요약")
print("=" * 80)

print("\n[Agent 모드 - 유의한 증가]")
agent_sig = df_results[(df_results['mode'] == 'Agent') & (df_results['p'] < 0.05)].sort_values('p')
if len(agent_sig) > 0:
    for _, row in agent_sig.iterrows():
        print(f"  {row['item']}: {row['first']:.2f} → {row['last']:.2f} ({row['change']:+.2f}, p={row['p']:.3f})")
else:
    print("  (유의한 항목 없음)")

print("\n[Freepass 모드 - 유의한 변화]")
free_sig = df_results[(df_results['mode'] == 'Freepass') & (df_results['p'] < 0.05)].sort_values('p')
if len(free_sig) > 0:
    for _, row in free_sig.iterrows():
        print(f"  {row['item']}: {row['first']:.2f} → {row['last']:.2f} ({row['change']:+.2f}, p={row['p']:.3f})")
else:
    print("  (유의한 항목 없음)")

print("\n" + "=" * 80)
print("🎉 분석 완료!")
print("=" * 80)

