#!/usr/bin/env python3
"""
LLM 3모델 평균 vs 교사 2명 평균 항목별 점수 비교
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

목적: LLM과 교사의 실제 점수를 항목별로 비교
"""

import pandas as pd
from scipy import stats
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════
# 1. 데이터 로드
# ═══════════════════════════════════════════════════════════════════════════

BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / 'data'
OUTPUT_DIR = BASE_DIR / 'scripts' / 'verification'

print("=" * 80)
print("📊 LLM vs 교사 항목별 점수 비교")
print("=" * 80)

# LLM 데이터
df_llm = pd.read_csv(DATA_DIR / 'llm_evaluations' / 'llm_284sessions_complete.csv')

# 교사 데이터
df_teacher_raw = pd.read_csv(DATA_DIR / 'analysis_results' / 'three_teachers_100_sessions.csv')
df_teacher = df_teacher_raw[df_teacher_raw['evaluator'].isin([96, 97])]

# 교사 평균
teacher_avg = df_teacher.groupby('session_id').agg({
    'overall': 'mean',
    'q1': 'mean', 'q2': 'mean', 'q3': 'mean',
    'r1': 'mean', 'r2': 'mean', 'r3': 'mean',
    'c1': 'mean', 'c2': 'mean',
    'q_total': 'mean', 'r_total': 'mean', 'c_total': 'mean'
}).reset_index()

# 병합
df_merged = pd.merge(df_llm, teacher_avg, on='session_id', how='inner')

print(f"\n✓ 공통 세션: {len(df_merged)}")

# ═══════════════════════════════════════════════════════════════════════════
# 2. 항목별 평균 비교
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("📊 항목별 점수 비교")
print("=" * 80)

items = [
    ('A1 수학전문성', 'avg_A1', 'q1', 5),
    ('A2 질문구조화', 'avg_A2', 'q2', 5),
    ('A3 학습맥락', 'avg_A3', 'q3', 5),
    ('B1 학습자맞춤', 'avg_B1', 'r1', 5),
    ('B2 설명체계성', 'avg_B2', 'r2', 5),
    ('B3 학습확장성', 'avg_B3', 'r3', 5),
    ('C1 대화일관성', 'avg_C1', 'c1', 5),
    ('C2 학습지원', 'avg_C2', 'c2', 5),
    ('전체', 'avg_overall', 'overall', 40)
]

results = []

for item_name, llm_col, teacher_col, max_score in items:
    llm_mean = df_merged[llm_col].mean()
    llm_std = df_merged[llm_col].std()
    
    teacher_mean = df_merged[teacher_col].mean()
    teacher_std = df_merged[teacher_col].std()
    
    diff = llm_mean - teacher_mean
    
    # t-test
    t_stat, p_val = stats.ttest_ind(df_merged[llm_col], df_merged[teacher_col])
    
    # 상관계수
    r, _ = stats.pearsonr(df_merged[llm_col], df_merged[teacher_col])
    
    results.append({
        '항목': item_name,
        'LLM_평균': round(llm_mean, 2),
        'LLM_SD': round(llm_std, 2),
        '교사_평균': round(teacher_mean, 2),
        '교사_SD': round(teacher_std, 2),
        '차이': round(diff, 2),
        't': round(t_stat, 2),
        'p': round(p_val, 3) if p_val >= 0.001 else '<0.001',
        'r': round(r, 3),
        '만점': max_score
    })
    
    print(f"{item_name:12s}: LLM={llm_mean:.2f}, 교사={teacher_mean:.2f}, "
          f"차이={diff:+.2f}, r={r:.3f}")

df_results = pd.DataFrame(results)

print("\n" + "=" * 80)
print("📋 전체 결과")
print("=" * 80)
print(df_results.to_string(index=False))

# ═══════════════════════════════════════════════════════════════════════════
# 3. 마크다운 표 생성
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("📝 마크다운 표")
print("=" * 80)

markdown = []
markdown.append("**[표Ⅴ-X] LLM-교사 평가 항목별 점수 비교 (N=100)**")
markdown.append("")
markdown.append("| 항목 | LLM 3모델 | 교사 2명 | 차이 | r | 비고 |")
markdown.append("|:----:|:---------:|:-------:|:----:|:-:|:----:|")

for _, row in df_results.iterrows():
    item = row['항목']
    llm = f"{row['LLM_평균']:.2f} ({row['LLM_SD']:.2f})"
    teacher = f"{row['교사_평균']:.2f} ({row['교사_SD']:.2f})"
    diff = f"{row['차이']:+.2f}"
    r = f"{row['r']:.3f}"
    max_score = f"{row['만점']}점"
    
    if item == '전체':
        markdown.append(f"| **{item}** | **{llm}** | **{teacher}** | **{diff}** | **{r}*** | {max_score} |")
    else:
        markdown.append(f"| {item} | {llm} | {teacher} | {diff} | {r}*** | {max_score} |")

markdown.append("")
markdown.append("주: 평균(표준편차). ***p<0.001. LLM은 Gemini, Claude, GPT-5 평균, 교사는 A, B 평균.")

markdown_text = "\n".join(markdown)
print(markdown_text)

# 저장
df_results.to_csv(OUTPUT_DIR / 'LLM_TEACHER_SCORE_COMPARISON.csv', index=False, encoding='utf-8-sig')

with open(OUTPUT_DIR / 'LLM_TEACHER_SCORE_COMPARISON.md', 'w', encoding='utf-8') as f:
    f.write(markdown_text)

print("\n" + "=" * 80)
print("✅ 완료!")
print("=" * 80)
print(f"\n파일:")
print(f"  - LLM_TEACHER_SCORE_COMPARISON.csv")
print(f"  - LLM_TEACHER_SCORE_COMPARISON.md")

# ═══════════════════════════════════════════════════════════════════════════
# 4. 핵심 발견
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("🎯 핵심 발견")
print("=" * 80)

# 가장 큰 차이
biggest_diff = df_results.loc[df_results['차이'].abs().idxmax()]
print(f"\n가장 큰 차이:")
print(f"  {biggest_diff['항목']}: {biggest_diff['차이']:+.2f}점")

# 가장 높은/낮은 상관
highest_r = df_results[df_results['항목'] != '전체'].loc[df_results[df_results['항목'] != '전체']['r'].idxmax()]
lowest_r = df_results[df_results['항목'] != '전체'].loc[df_results[df_results['항목'] != '전체']['r'].idxmin()]

print(f"\n가장 높은 상관:")
print(f"  {highest_r['항목']}: r={highest_r['r']:.3f}")

print(f"\n가장 낮은 상관:")
print(f"  {lowest_r['항목']}: r={lowest_r['r']:.3f}")

