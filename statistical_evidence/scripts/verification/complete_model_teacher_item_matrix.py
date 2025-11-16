#!/usr/bin/env python3
"""
모델별 × 교사별 × 항목별 완전 매트릭스
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

계산: 3모델 × 2교사 × 8항목 = 48개 조합
"""

import pandas as pd
from scipy import stats
from pathlib import Path
import numpy as np

# ═══════════════════════════════════════════════════════════════════════════
# 1. 데이터 로드
# ═══════════════════════════════════════════════════════════════════════════

BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / 'data'
OUTPUT_DIR = BASE_DIR / 'scripts' / 'verification'

print("=" * 80)
print("📊 모델별 × 교사별 × 항목별 완전 매트릭스")
print("=" * 80)

# LLM 데이터
df_llm = pd.read_csv(DATA_DIR / 'llm_evaluations' / 'llm_284sessions_complete.csv')

# 교사 데이터
df_teacher_raw = pd.read_csv(DATA_DIR / 'analysis_results' / 'three_teachers_100_sessions.csv')

print(f"\n✓ LLM 세션: {len(df_llm)}")
print(f"✓ 교사 데이터: {len(df_teacher_raw)} 행")

# ═══════════════════════════════════════════════════════════════════════════
# 2. 완전 매트릭스 계산
# ═══════════════════════════════════════════════════════════════════════════

items = [
    ('A1', 'q1'),
    ('A2', 'q2'),
    ('A3', 'q3'),
    ('B1', 'r1'),
    ('B2', 'r2'),
    ('B3', 'r3'),
    ('C1', 'c1'),
    ('C2', 'c2')
]

models = ['openai', 'anthropic', 'gemini']
teachers = [96, 97]

results = []

for model in models:
    print(f"\n{'=' * 80}")
    print(f"모델: {model.upper()}")
    print(f"{'=' * 80}")
    
    for teacher_id in teachers:
        print(f"\n  교사 {teacher_id}:")
        
        # 해당 교사 데이터
        df_teacher = df_teacher_raw[df_teacher_raw['evaluator'] == teacher_id]
        
        # 병합
        df_merged = pd.merge(df_llm, df_teacher, on='session_id', how='inner')
        
        print(f"    공통 세션: {len(df_merged)}")
        
        # 항목별 상관
        for item_code, teacher_col in items:
            llm_col = f'{model}_{item_code}'
            
            if len(df_merged) > 0:
                r, p = stats.pearsonr(df_merged[llm_col], df_merged[teacher_col])
                
                # 유의성
                if p < 0.001:
                    sig = '***'
                elif p < 0.01:
                    sig = '**'
                elif p < 0.05:
                    sig = '*'
                else:
                    sig = ''
                
                results.append({
                    '모델': model.upper(),
                    '교사': f'교사 {teacher_id}',
                    '항목': item_code,
                    'r': round(r, 3),
                    'p': '<0.001' if p < 0.001 else round(p, 3),
                    'sig': sig
                })
                
                print(f"      {item_code}: r={r:.3f}{sig}")

df_results = pd.DataFrame(results)

# ═══════════════════════════════════════════════════════════════════════════
# 3. 피벗 테이블 (모델별로)
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("📋 모델별 피벗 테이블")
print("=" * 80)

for model in ['OPENAI', 'ANTHROPIC', 'GEMINI']:
    model_data = df_results[df_results['모델'] == model]
    pivot = model_data.pivot(index='항목', columns='교사', values='r')
    
    print(f"\n{model}:")
    print(pivot.to_string())

# ═══════════════════════════════════════════════════════════════════════════
# 4. 마크다운 표 생성 (모델별로 3개 표)
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("📝 마크다운 표 (모델별)")
print("=" * 80)

markdown_tables = []

for model in ['OPENAI', 'ANTHROPIC', 'GEMINI']:
    model_data = df_results[df_results['모델'] == model]
    
    markdown = []
    markdown.append(f"**{model}와 교사 A, B의 항목별 상관**")
    markdown.append("")
    markdown.append("| 항목 | 교사 A(96) | 교사 B(97) |")
    markdown.append("|:----:|:----------:|:----------:|")
    
    for item_code in ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2']:
        row_a = model_data[(model_data['항목'] == item_code) & (model_data['교사'] == '교사 96')]
        row_b = model_data[(model_data['항목'] == item_code) & (model_data['교사'] == '교사 97')]
        
        if len(row_a) > 0 and len(row_b) > 0:
            r_a = row_a.iloc[0]['r']
            sig_a = row_a.iloc[0]['sig']
            r_b = row_b.iloc[0]['r']
            sig_b = row_b.iloc[0]['sig']
            
            markdown.append(f"| {item_code} | {r_a:.3f}{sig_a} | {r_b:.3f}{sig_b} |")
    
    markdown.append("")
    markdown_tables.append("\n".join(markdown))
    print("\n".join(markdown))
    print("")

# ═══════════════════════════════════════════════════════════════════════════
# 5. 통합 표 (한 표에 모두)
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("📝 통합 마크다운 표")
print("=" * 80)

integrated = []
integrated.append("**[표Ⅴ-13c] 모델별 교사별 항목별 상관관계 (N=100)**")
integrated.append("")
integrated.append("| 항목 | OpenAI×A | OpenAI×B | Anthropic×A | Anthropic×B | Gemini×A | Gemini×B |")
integrated.append("|:----:|:--------:|:--------:|:-----------:|:-----------:|:--------:|:--------:|")

for item_code in ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2']:
    row_values = []
    
    for model in ['OPENAI', 'ANTHROPIC', 'GEMINI']:
        for teacher_id in [96, 97]:
            data = df_results[
                (df_results['모델'] == model) & 
                (df_results['교사'] == f'교사 {teacher_id}') &
                (df_results['항목'] == item_code)
            ]
            
            if len(data) > 0:
                r = data.iloc[0]['r']
                sig = data.iloc[0]['sig']
                row_values.append(f"{r:.3f}{sig}")
            else:
                row_values.append("-")
    
    integrated.append(f"| {item_code} | {' | '.join(row_values)} |")

integrated.append("")
integrated.append("주: ***p<0.001, **p<0.01, *p<0.05. N=100. A=교사 96, B=교사 97.")

integrated_text = "\n".join(integrated)
print(integrated_text)

# ═══════════════════════════════════════════════════════════════════════════
# 6. 저장
# ═══════════════════════════════════════════════════════════════════════════

df_results.to_csv(OUTPUT_DIR / 'COMPLETE_CORRELATION_MATRIX.csv', index=False, encoding='utf-8-sig')

with open(OUTPUT_DIR / 'COMPLETE_CORRELATION_MATRIX.md', 'w', encoding='utf-8') as f:
    f.write(integrated_text)
    f.write("\n\n---\n\n")
    f.write("\n\n---\n\n".join(markdown_tables))

print("\n" + "=" * 80)
print("✅ 저장 완료!")
print("=" * 80)
print(f"\n파일:")
print(f"  - COMPLETE_CORRELATION_MATRIX.csv")
print(f"  - COMPLETE_CORRELATION_MATRIX.md")

# ═══════════════════════════════════════════════════════════════════════════
# 7. 핵심 발견
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("🎯 핵심 발견")
print("=" * 80)

# 가장 높은/낮은 상관
highest = df_results.loc[df_results['r'].idxmax()]
lowest = df_results.loc[df_results['r'].idxmin()]

print(f"\n🔝 가장 높은 상관:")
print(f"   {highest['모델']} × {highest['교사']} × {highest['항목']}")
print(f"   r={highest['r']:.3f}")

print(f"\n🔻 가장 낮은 상관:")
print(f"   {lowest['모델']} × {lowest['교사']} × {lowest['항목']}")
print(f"   r={lowest['r']:.3f}")

# 모델별 평균
print(f"\n📊 모델별 평균:")
for model in ['OPENAI', 'ANTHROPIC', 'GEMINI']:
    model_avg = df_results[df_results['모델'] == model]['r'].mean()
    print(f"   {model}: {model_avg:.3f}")

