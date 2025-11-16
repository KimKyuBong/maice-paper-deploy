#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM-교사 상관관계 완전 분석
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from scipy import stats
from datetime import datetime

# 경로 설정
BASE_DIR = Path(__file__).parent.parent
RESULTS_DIR = BASE_DIR / "03_correlation_analysis" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# 소스 파일
LLM_FILE = BASE_DIR / "01_llm_scoring" / "results" / "llm_3models_averaged_perfect.csv"
TEACHER_FILE = BASE_DIR / "02_teacher_scoring" / "results" / "teacher_averaged_scores_perfect.csv"

print(f"{'='*80}")
print(f"LLM-교사 상관관계 완전 분석")
print(f"{'='*80}")
print(f"LLM 데이터: {LLM_FILE.name}")
print(f"교사 데이터: {TEACHER_FILE.name}")
print(f"시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*80}\n")

# [1] 데이터 로드
print("[1] 데이터 로드...")
df_llm = pd.read_csv(LLM_FILE)
df_teacher = pd.read_csv(TEACHER_FILE)

print(f"✓ LLM: {len(df_llm)}개 세션")
print(f"✓ 교사: {len(df_teacher)}개 세션\n")

# [2] 데이터 병합
print("[2] 데이터 병합...")

# 세션 ID로 병합
df_merged = pd.merge(
    df_llm,
    df_teacher,
    left_on='session_id',
    right_on='session_id',
    how='inner'
)

print(f"✓ 공통 세션: {len(df_merged)}개\n")

if len(df_merged) == 0:
    print("⚠️  공통 세션이 없습니다!")
    exit(1)

# [3] 매핑 정의
print("[3] 상관관계 분석...")

# LLM-교사 매핑
mappings = {
    'question': {
        'llm_col': 'avg_question_total',
        'teacher_col': 'teacher_question_total',
        'name': '질문 (A)'
    },
    'answer': {
        'llm_col': 'avg_answer_total',
        'teacher_col': 'teacher_answer_total',
        'name': '답변 (B)'
    },
    'context': {
        'llm_col': 'avg_context_total',
        'teacher_col': 'teacher_context_total',
        'name': '맥락 (C)'
    },
    'overall': {
        'llm_col': 'avg_overall',
        'teacher_col': 'teacher_overall',
        'name': '전체'
    }
}

# 상관관계 계산
correlations = {}
for key, mapping in mappings.items():
    llm_col = mapping['llm_col']
    teacher_col = mapping['teacher_col']
    
    # 컬럼 존재 확인
    if llm_col in df_merged.columns and teacher_col in df_merged.columns:
        # 결측치 제거
        valid_data = df_merged[[llm_col, teacher_col]].dropna()
        
        if len(valid_data) >= 3:
            # Pearson 상관
            pearson_r, pearson_p = stats.pearsonr(valid_data[llm_col], valid_data[teacher_col])
            
            # Spearman 상관
            spearman_r, spearman_p = stats.spearmanr(valid_data[llm_col], valid_data[teacher_col])
            
            correlations[key] = {
                'name': mapping['name'],
                'n': int(len(valid_data)),
                'pearson': {
                    'r': float(pearson_r),
                    'p': float(pearson_p),
                    'significant': bool(pearson_p < 0.05)
                },
                'spearman': {
                    'r': float(spearman_r),
                    'p': float(spearman_p),
                    'significant': bool(spearman_p < 0.05)
                },
                'llm_mean': float(valid_data[llm_col].mean()),
                'llm_std': float(valid_data[llm_col].std()),
                'teacher_mean': float(valid_data[teacher_col].mean()),
                'teacher_std': float(valid_data[teacher_col].std())
            }
        else:
            correlations[key] = {
                'name': mapping['name'],
                'n': 0,
                'error': '데이터 부족'
            }
    else:
        missing = []
        if llm_col not in df_merged.columns:
            missing.append(f"LLM:{llm_col}")
        if teacher_col not in df_merged.columns:
            missing.append(f"교사:{teacher_col}")
        
        correlations[key] = {
            'name': mapping['name'],
            'error': f'컬럼 없음: {", ".join(missing)}'
        }

print(f"✓ {len(correlations)}개 카테고리 상관분석 완료\n")

# [4] 중분류 상관분석
print("[4] 중분류 상관분석...")

# LLM 중분류
llm_mid_cats = {
    'A1': 'avg_A1_total',
    'A2': 'avg_A2_total',
    'A3': 'avg_A3_total',
    'B1': 'avg_B1_total',
    'B2': 'avg_B2_total',
    'B3': 'avg_B3_total',
    'C1': 'avg_C1_total',
    'C2': 'avg_C2_total'
}

# 교사 중분류 (8개)
teacher_mid_cats = {
    'A1': 'teacher_question_professionalism',
    'A2': 'teacher_question_structuring',
    'A3': 'teacher_question_context',
    'B1': 'teacher_answer_customization',
    'B2': 'teacher_answer_systematicity',
    'B3': 'teacher_answer_expandability',
    'C1': 'teacher_context_dialogue',
    'C2': 'teacher_context_support'
}

mid_correlations = {}
for cat_code in llm_mid_cats.keys():
    llm_col = llm_mid_cats[cat_code]
    teacher_col = teacher_mid_cats[cat_code]
    
    if llm_col in df_merged.columns and teacher_col in df_merged.columns:
        valid_data = df_merged[[llm_col, teacher_col]].dropna()
        
        if len(valid_data) >= 3:
            pearson_r, pearson_p = stats.pearsonr(valid_data[llm_col], valid_data[teacher_col])
            
            mid_correlations[cat_code] = {
                'n': int(len(valid_data)),
                'pearson_r': float(pearson_r),
                'pearson_p': float(pearson_p),
                'significant': bool(pearson_p < 0.05)
            }

print(f"✓ {len(mid_correlations)}개 중분류 상관분석 완료\n")

# [5] 결과 저장
print("[5] 결과 저장...")

# 대분류 상관
corr_file = RESULTS_DIR / "llm_teacher_correlations_perfect.json"
with open(corr_file, 'w', encoding='utf-8') as f:
    json.dump(correlations, f, ensure_ascii=False, indent=2)
print(f"✓ {corr_file.name}")

# 중분류 상관
mid_corr_file = RESULTS_DIR / "llm_teacher_mid_correlations_perfect.json"
with open(mid_corr_file, 'w', encoding='utf-8') as f:
    json.dump(mid_correlations, f, ensure_ascii=False, indent=2)
print(f"✓ {mid_corr_file.name}")

# 병합 데이터
merged_file = RESULTS_DIR / "llm_teacher_merged_perfect.csv"
df_merged.to_csv(merged_file, index=False, encoding='utf-8')
print(f"✓ {merged_file.name}")

# 요약
summary = {
    "분석시각": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    "총세션": len(df_merged),
    "대분류_상관": {
        key: {
            'pearson_r': float(data.get('pearson', {}).get('r', 0)),
            'significant': bool(data.get('pearson', {}).get('significant', False))
        }
        for key, data in correlations.items()
        if 'pearson' in data
    },
    "평균_상관": np.mean([
        data.get('pearson', {}).get('r', 0)
        for data in correlations.values()
        if 'pearson' in data
    ])
}

summary_file = RESULTS_DIR / "correlation_summary_perfect.json"
with open(summary_file, 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
print(f"✓ {summary_file.name}\n")

# 최종 출력
print(f"{'='*80}")
print(f"상관관계 분석 완료!")
print(f"{'='*80}")
print(f"\n주요 결과:")
print(f"  • 공통 세션 수: {len(df_merged)}")
print(f"\n대분류 상관계수 (Pearson r):")
for key, data in correlations.items():
    if 'pearson' in data:
        r = data['pearson']['r']
        p = data['pearson']['p']
        sig = "**" if p < 0.01 else "*" if p < 0.05 else ""
        print(f"  • {data['name']:12s}: r={r:+.3f} (p={p:.3f}) {sig}")

print(f"\n평균 상관계수: {summary['평균_상관']:.3f}")

if mid_correlations:
    print(f"\n중분류 평균 상관: {np.mean([v['pearson_r'] for v in mid_correlations.values()]):.3f}")

print(f"\n결과 위치: {RESULTS_DIR}")
print(f"{'='*80}\n")

