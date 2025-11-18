#!/usr/bin/env python3
"""
교사 평가자 간 신뢰도 계산 (ICC, Pearson, Spearman)
표V-8: 교사 평가자 간 신뢰도 (N=100)
"""

import json
import pandas as pd
import numpy as np
from scipy import stats
import pingouin as pg
from pathlib import Path

# 경로 설정
BASE = Path(__file__).parent.parent
DATA_FILE = BASE / 'data' / 'teacher_evaluations' / 'latest_evaluations.json'
RESULTS_DIR = Path(__file__).parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

print("="*80)
print("표V-8: 교사 평가자 간 신뢰도 계산")
print("="*80)
print()

# 1. 데이터 로드
print("[1] 데이터 로드...")
with open(DATA_FILE, 'r') as f:
    data = json.load(f)

df = pd.DataFrame(data)

# 필요한 컬럼만 추출
df = df[['conversation_session_id', 'evaluated_by', 'overall_score', 
         'question_total_score', 'response_total_score', 'context_total_score']].copy()

df.columns = ['session_id', 'teacher_id', 'overall_score', 
              'question_total', 'response_total', 'context_total']

print(f"✓ 총 레코드: {len(df)}")
print(f"✓ 교사 ID: {sorted(df['teacher_id'].unique())}")
print(f"✓ 세션 수: {df['session_id'].nunique()}")
print()

# 2. 교사별 데이터 분리 (상관계수 계산용)
print("[2] 교사별 데이터 분리...")
teacher_96 = df[df['teacher_id'] == 96].sort_values('session_id').reset_index(drop=True)
teacher_97 = df[df['teacher_id'] == 97].sort_values('session_id').reset_index(drop=True)

print(f"✓ 교사 96: {len(teacher_96)}개 세션")
print(f"✓ 교사 97: {len(teacher_97)}개 세션")
print()

# 3. ICC 계산 함수
def calculate_icc(df, score_col):
    """ICC(2,k) 계산 - Two-way random effects, average measures"""
    df_icc = df[['session_id', 'teacher_id', score_col]].copy()
    df_icc.columns = ['session', 'rater', 'score']
    
    icc_result = pg.intraclass_corr(data=df_icc, targets='session', raters='rater', ratings='score')
    icc_2k = icc_result[icc_result['Type'] == 'ICC2k']
    
    return {
        'ICC': float(icc_2k['ICC'].values[0]),
        'CI95_lower': float(icc_2k['CI95%'].values[0][0]),
        'CI95_upper': float(icc_2k['CI95%'].values[0][1]),
        'F': float(icc_2k['F'].values[0]),
        'pval': float(icc_2k['pval'].values[0])
    }

# 4. 상관계수 계산 함수
def calculate_correlations(teacher_96, teacher_97, score_col):
    """Pearson과 Spearman 상관계수 계산"""
    scores_96 = teacher_96[score_col].values
    scores_97 = teacher_97[score_col].values
    
    pearson_r, pearson_p = stats.pearsonr(scores_96, scores_97)
    spearman_rho, spearman_p = stats.spearmanr(scores_96, scores_97)
    
    return {
        'pearson_r': float(pearson_r),
        'pearson_p': float(pearson_p),
        'spearman_rho': float(spearman_rho),
        'spearman_p': float(spearman_p),
        'n': len(scores_96)
    }

# 5. 각 영역별 계산
print("[3] ICC 및 상관계수 계산...")
print()

categories = {
    '전체 점수': 'overall_score',
    '질문 영역': 'question_total',
    '응답 영역': 'response_total',
    '맥락 영역': 'context_total'
}

results = {}

for name, col in categories.items():
    print(f"【{name}】")
    
    # ICC 계산
    icc_result = calculate_icc(df, col)
    
    # 상관계수 계산
    corr_result = calculate_correlations(teacher_96, teacher_97, col)
    
    # 결과 통합
    results[name] = {
        **icc_result,
        **corr_result
    }
    
    print(f"  ICC(2,k) = {icc_result['ICC']:.3f} (95% CI [{icc_result['CI95_lower']:.2f}, {icc_result['CI95_upper']:.2f}])")
    print(f"  Pearson r = {corr_result['pearson_r']:.3f} (p={corr_result['pearson_p']:.6f})")
    print(f"  Spearman ρ = {corr_result['spearman_rho']:.3f} (p={corr_result['spearman_p']:.6f})")
    
    if icc_result['pval'] < 0.001:
        sig = "***"
    elif icc_result['pval'] < 0.01:
        sig = "**"
    elif icc_result['pval'] < 0.05:
        sig = "*"
    else:
        sig = "n.s."
    print(f"  유의성: {sig}")
    print()

# 6. 결과 저장
print("[4] 결과 저장...")

output_file = RESULTS_DIR / 'table_v8_teacher_icc.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        'table': '표Ⅴ-8',
        'title': '교사 평가자 간 신뢰도',
        'n_sessions': df['session_id'].nunique(),
        'n_teachers': 2,
        'teacher_ids': [96, 97],
        'results': results,
        'interpretation': {
            'overall_icc': results['전체 점수']['ICC'],
            'koo_li_2016_threshold': {
                'poor': '<0.50',
                'moderate': '0.50-0.75',
                'good': '0.75-0.90',
                'excellent': '>0.90'
            },
            'current_level': 'moderate-good' if results['전체 점수']['ICC'] < 0.75 else 'good'
        }
    }, f, ensure_ascii=False, indent=2)

print(f"✓ {output_file}")
print()

# 7. 표 형식 출력
print("="*80)
print("표V-8 형식 출력")
print("="*80)
print()
print("| 측정 방법 | 전체 점수 | 질문 영역 | 응답 영역 | 맥락 영역 |")
print("|:--------:|:---------:|:---------:|:---------:|:---------:|")

# ICC 행
icc_row = "| **ICC(2,k)** |"
for name in ['전체 점수', '질문 영역', '응답 영역', '맥락 영역']:
    icc_val = results[name]['ICC']
    p_val = results[name]['pval']
    if p_val < 0.001:
        sig = "***"
    elif p_val < 0.01:
        sig = "**"
    elif p_val < 0.05:
        sig = "*"
    else:
        sig = ""
    icc_row += f" **{icc_val:.3f}{sig}** |"
print(icc_row)

# Pearson 행
pearson_row = "| Pearson r |"
for name in ['전체 점수', '질문 영역', '응답 영역', '맥락 영역']:
    r_val = results[name]['pearson_r']
    p_val = results[name]['pearson_p']
    if p_val < 0.001:
        sig = "***"
    elif p_val < 0.01:
        sig = "**"
    elif p_val < 0.05:
        sig = "*"
    else:
        sig = ""
    pearson_row += f" {r_val:.3f}{sig} |"
print(pearson_row)

# Spearman 행
spearman_row = "| Spearman ρ |"
for name in ['전체 점수', '질문 영역', '응답 영역', '맥락 영역']:
    rho_val = results[name]['spearman_rho']
    p_val = results[name]['spearman_p']
    if p_val < 0.001:
        sig = "***"
    elif p_val < 0.01:
        sig = "**"
    elif p_val < 0.05:
        sig = "*"
    else:
        sig = ""
    spearman_row += f" {rho_val:.3f}{sig} |"
print(spearman_row)

print()
print("="*80)
print("✅ 교사 평가자 간 신뢰도 계산 완료!")
print("="*80)
print()
print(f"결과 파일: {output_file}")
print()


