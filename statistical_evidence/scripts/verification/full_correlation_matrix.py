#!/usr/bin/env python3
"""
LLM 모델별 × 교사별 상관관계 완전 매트릭스
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

계산:
  - LLM: OpenAI, Anthropic, Gemini, 3모델 평균
  - 교사: 96, 97, 2명 평균
  - 전체 조합 매트릭스
"""

import pandas as pd
from scipy import stats
from pathlib import Path
import json

# ═══════════════════════════════════════════════════════════════════════════
# 1. 데이터 로드
# ═══════════════════════════════════════════════════════════════════════════

BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / 'data'
OUTPUT_DIR = BASE_DIR / 'scripts' / 'verification'

print("=" * 80)
print("📊 LLM-교사 상관관계 완전 매트릭스")
print("=" * 80)

# LLM 데이터
df_llm = pd.read_csv(DATA_DIR / 'llm_evaluations' / 'llm_284sessions_complete.csv')

# 각 모델별 Total 계산
for model in ['gemini', 'anthropic', 'openai']:
    cols = [f'{model}_A1', f'{model}_A2', f'{model}_A3', 
            f'{model}_B1', f'{model}_B2', f'{model}_B3', 
            f'{model}_C1', f'{model}_C2']
    df_llm[f'{model}_total'] = df_llm[cols].sum(axis=1)

# 3모델 평균
df_llm['avg_total'] = df_llm['avg_overall']

# 교사 데이터
df_teacher = pd.read_csv(DATA_DIR / 'analysis_results' / 'three_teachers_100_sessions.csv')
df_teacher_96_97 = df_teacher[df_teacher['evaluator'].isin([96, 97])]

print(f"\n✓ LLM 데이터: {len(df_llm)} 세션")
print(f"✓ 교사 데이터: {len(df_teacher_96_97)} 행 (교사 96, 97)")

# ═══════════════════════════════════════════════════════════════════════════
# 2. 교사별 데이터 준비
# ═══════════════════════════════════════════════════════════════════════════

# 교사 96
teacher_96 = df_teacher_96_97[df_teacher_96_97['evaluator'] == 96][['session_id', 'overall']]
teacher_96.columns = ['session_id', 'teacher_96']

# 교사 97
teacher_97 = df_teacher_96_97[df_teacher_96_97['evaluator'] == 97][['session_id', 'overall']]
teacher_97.columns = ['session_id', 'teacher_97']

# 교사 2명 평균
teacher_avg = df_teacher_96_97.groupby('session_id')['overall'].mean().reset_index()
teacher_avg.columns = ['session_id', 'teacher_avg']

print(f"\n✓ 교사 96: {len(teacher_96)} 세션")
print(f"✓ 교사 97: {len(teacher_97)} 세션")
print(f"✓ 교사 평균: {len(teacher_avg)} 세션")

# ═══════════════════════════════════════════════════════════════════════════
# 3. 완전 매트릭스 계산
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("📊 완전 상관관계 매트릭스")
print("=" * 80)

llm_models = [
    ('OpenAI', 'openai_total'),
    ('Anthropic', 'anthropic_total'),
    ('Gemini', 'gemini_total'),
    ('LLM 3모델 평균', 'avg_total')
]

teachers = [
    ('교사 96', teacher_96, 'teacher_96'),
    ('교사 97', teacher_97, 'teacher_97'),
    ('교사 2명 평균', teacher_avg, 'teacher_avg')
]

results = []

for llm_name, llm_col in llm_models:
    print(f"\n{llm_name}:")
    print("-" * 80)
    
    for teacher_name, teacher_df, teacher_col in teachers:
        # 병합
        merged = pd.merge(df_llm[['session_id', llm_col]], teacher_df, on='session_id', how='inner')
        
        if len(merged) > 0:
            # 상관계수
            r, p = stats.pearsonr(merged[llm_col], merged[teacher_col])
            
            results.append({
                'LLM': llm_name,
                '교사': teacher_name,
                'N': len(merged),
                'Pearson_r': round(r, 3),
                'p': '<0.001' if p < 0.001 else round(p, 3)
            })
            
            print(f"  {teacher_name:15s}: N={len(merged):3d}, r={r:.3f}, p={p:.6f}")
        else:
            print(f"  {teacher_name:15s}: 데이터 없음")

# ═══════════════════════════════════════════════════════════════════════════
# 4. 결과 정리
# ═══════════════════════════════════════════════════════════════════════════

df_results = pd.DataFrame(results)

print("\n" + "=" * 80)
print("📋 전체 결과 표")
print("=" * 80)
print(df_results.to_string(index=False))

# 피벗 테이블
pivot = df_results.pivot(index='LLM', columns='교사', values='Pearson_r')

print("\n" + "=" * 80)
print("📊 피벗 테이블 (상관계수)")
print("=" * 80)
print(pivot)

# 저장
df_results.to_csv(OUTPUT_DIR / 'LLM_TEACHER_CORRELATION_MATRIX.csv', 
                  index=False, encoding='utf-8-sig')

pivot.to_csv(OUTPUT_DIR / 'LLM_TEACHER_CORRELATION_PIVOT.csv', 
             encoding='utf-8-sig')

# JSON으로도 저장
results_dict = {
    'full_matrix': results,
    'summary': {
        'highest_correlation': df_results.loc[df_results['Pearson_r'].idxmax()].to_dict(),
        'lowest_correlation': df_results.loc[df_results['Pearson_r'].idxmin()].to_dict(),
        'avg_3model_avg_2teacher': df_results[
            (df_results['LLM'] == 'LLM 3모델 평균') & 
            (df_results['교사'] == '교사 2명 평균')
        ].iloc[0].to_dict() if len(df_results[
            (df_results['LLM'] == 'LLM 3모델 평균') & 
            (df_results['교사'] == '교사 2명 평균')
        ]) > 0 else None
    }
}

with open(OUTPUT_DIR / 'LLM_TEACHER_CORRELATION_FULL.json', 'w', encoding='utf-8') as f:
    json.dump(results_dict, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 80)
print("✅ 저장 완료!")
print("=" * 80)
print(f"\n파일:")
print(f"  - LLM_TEACHER_CORRELATION_MATRIX.csv")
print(f"  - LLM_TEACHER_CORRELATION_PIVOT.csv")
print(f"  - LLM_TEACHER_CORRELATION_FULL.json")

# ═══════════════════════════════════════════════════════════════════════════
# 5. 핵심 발견
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("🎯 핵심 발견")
print("=" * 80)

# 3모델 평균 vs 2명 평균
key_result = df_results[
    (df_results['LLM'] == 'LLM 3모델 평균') & 
    (df_results['교사'] == '교사 2명 평균')
]

if len(key_result) > 0:
    key_r = key_result.iloc[0]['Pearson_r']
    key_n = key_result.iloc[0]['N']
    print(f"\n📌 논문 핵심 값:")
    print(f"   LLM 3모델 평균 vs 교사 2명 평균")
    print(f"   r={key_r:.3f}, N={key_n}")

# 가장 높은/낮은 상관
highest = df_results.loc[df_results['Pearson_r'].idxmax()]
lowest = df_results.loc[df_results['Pearson_r'].idxmin()]

print(f"\n🔝 가장 높은 상관:")
print(f"   {highest['LLM']} × {highest['교사']}")
print(f"   r={highest['Pearson_r']:.3f}, N={highest['N']}")

print(f"\n🔻 가장 낮은 상관:")
print(f"   {lowest['LLM']} × {lowest['교사']}")
print(f"   r={lowest['Pearson_r']:.3f}, N={lowest['N']}")

