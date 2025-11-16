#!/usr/bin/env python3
"""
모델별 × 항목별 상관관계 완전 매트릭스
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

목적: 각 LLM 모델이 어떤 항목에서 교사와 일치하는지 분석

매트릭스:
  - 행: A1~C2 (8개 항목)
  - 열: OpenAI, Anthropic, Gemini, 3모델 평균
  - 값: 교사 2명 평균과의 상관계수
"""

import pandas as pd
from scipy import stats
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

# ═══════════════════════════════════════════════════════════════════════════
# 1. 데이터 로드
# ═══════════════════════════════════════════════════════════════════════════

BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / 'data'
OUTPUT_DIR = BASE_DIR / 'scripts' / 'verification'

print("=" * 80)
print("📊 모델별 × 항목별 상관관계 완전 매트릭스")
print("=" * 80)

# LLM 데이터
df_llm = pd.read_csv(DATA_DIR / 'llm_evaluations' / 'llm_284sessions_complete.csv')

# 교사 데이터
df_teacher_raw = pd.read_csv(DATA_DIR / 'analysis_results' / 'three_teachers_100_sessions.csv')
df_teacher = df_teacher_raw[df_teacher_raw['evaluator'].isin([96, 97])]

# 교사 평균
teacher_avg = df_teacher.groupby('session_id').agg({
    'q1': 'mean', 'q2': 'mean', 'q3': 'mean',
    'r1': 'mean', 'r2': 'mean', 'r3': 'mean',
    'c1': 'mean', 'c2': 'mean'
}).reset_index()

# 병합
df_merged = pd.merge(df_llm, teacher_avg, on='session_id', how='inner')

print(f"\n✓ 공통 세션: {len(df_merged)}")

# ═══════════════════════════════════════════════════════════════════════════
# 2. 모델별 × 항목별 상관계수 계산
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("📊 모델별 × 항목별 상관계수")
print("=" * 80)

items = [
    ('A1 수학전문성', 'A1', 'q1'),
    ('A2 질문구조화', 'A2', 'q2'),
    ('A3 학습맥락', 'A3', 'q3'),
    ('B1 학습자맞춤', 'B1', 'r1'),
    ('B2 설명체계성', 'B2', 'r2'),
    ('B3 학습확장성', 'B3', 'r3'),
    ('C1 대화일관성', 'C1', 'c1'),
    ('C2 학습지원', 'C2', 'c2')
]

models = [
    ('OpenAI', 'openai'),
    ('Anthropic', 'anthropic'),
    ('Gemini', 'gemini'),
    ('3모델 평균', 'avg')
]

# 매트릭스 계산
matrix = []

for item_name, item_code, teacher_col in items:
    row = {'항목': item_name}
    
    print(f"\n{item_name}:")
    
    for model_name, model_prefix in models:
        llm_col = f'{model_prefix}_{item_code}'
        
        r, p = stats.pearsonr(df_merged[llm_col], df_merged[teacher_col])
        
        row[model_name] = round(r, 3)
        
        # 유의성 표시
        if p < 0.001:
            sig = '***'
        elif p < 0.01:
            sig = '**'
        elif p < 0.05:
            sig = '*'
        else:
            sig = ''
        
        print(f"  {model_name:12s}: r={r:.3f}{sig} (p={p:.4f})")
    
    matrix.append(row)

df_matrix = pd.DataFrame(matrix)

print("\n" + "=" * 80)
print("📋 완전 매트릭스")
print("=" * 80)
print(df_matrix.to_string(index=False))

# ═══════════════════════════════════════════════════════════════════════════
# 3. 마크다운 표 생성
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("📝 마크다운 표")
print("=" * 80)

markdown = []
markdown.append("**[표Ⅴ-13c] 모델별 항목별 교사와의 상관관계 (N=100)**")
markdown.append("")
markdown.append("| 항목 | OpenAI | Anthropic | Gemini | 3모델 평균 |")
markdown.append("|:----:|:------:|:---------:|:------:|:---------:|")

for _, row in df_matrix.iterrows():
    item = row['항목']
    openai = f"{row['OpenAI']:.3f}"
    anthropic = f"{row['Anthropic']:.3f}"
    gemini = f"{row['Gemini']:.3f}"
    avg = f"{row['3모델 평균']:.3f}"
    
    markdown.append(f"| {item} | {openai}*** | {anthropic}*** | {gemini}*** | {avg}*** |")

markdown.append("")
markdown.append("주: ***p<0.001. 각 LLM 모델과 교사 2명(A, B) 평균과의 Pearson 상관계수. N=100.")

markdown_text = "\n".join(markdown)
print(markdown_text)

# ═══════════════════════════════════════════════════════════════════════════
# 4. 히트맵 생성
# ═══════════════════════════════════════════════════════════════════════════

fig, ax = plt.subplots(1, 1, figsize=(10, 6))

# 데이터 준비
heatmap_data = df_matrix.set_index('항목')[['OpenAI', 'Anthropic', 'Gemini', '3모델 평균']]

# 히트맵
sns.heatmap(heatmap_data, annot=True, fmt='.3f', cmap='YlGnBu', 
            cbar_kws={'label': 'Pearson r'}, vmin=0.2, vmax=0.8,
            linewidths=0.5, ax=ax)

ax.set_title('모델별 × 항목별 교사와의 상관관계', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('LLM 모델', fontsize=12, fontweight='bold')
ax.set_ylabel('평가 항목', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'model_item_correlation_heatmap.png', dpi=300, bbox_inches='tight')
print(f"\n✓ 저장: model_item_correlation_heatmap.png")

# ═══════════════════════════════════════════════════════════════════════════
# 5. 분석 요약
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("📊 분석 요약")
print("=" * 80)

# 모델별 평균
for model in ['OpenAI', 'Anthropic', 'Gemini', '3모델 평균']:
    model_avg = df_matrix[model].mean()
    model_max = df_matrix[model].max()
    model_min = df_matrix[model].min()
    
    max_item = df_matrix.loc[df_matrix[model].idxmax(), '항목']
    min_item = df_matrix.loc[df_matrix[model].idxmin(), '항목']
    
    print(f"\n{model}:")
    print(f"  평균 r: {model_avg:.3f}")
    print(f"  최고: {max_item} (r={model_max:.3f})")
    print(f"  최저: {min_item} (r={model_min:.3f})")

# CSV 저장
df_matrix.to_csv(OUTPUT_DIR / 'MODEL_ITEM_CORRELATION_MATRIX.csv', index=False, encoding='utf-8-sig')

with open(OUTPUT_DIR / 'MODEL_ITEM_CORRELATION_MATRIX.md', 'w', encoding='utf-8') as f:
    f.write(markdown_text)

print("\n" + "=" * 80)
print("✅ 완료!")
print("=" * 80)
print(f"\n파일:")
print(f"  - MODEL_ITEM_CORRELATION_MATRIX.csv")
print(f"  - MODEL_ITEM_CORRELATION_MATRIX.md")
print(f"  - model_item_correlation_heatmap.png")

