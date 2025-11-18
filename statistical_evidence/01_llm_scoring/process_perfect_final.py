#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM 3모델 PERFECT FINAL 데이터 분석
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime

# 경로 설정
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "llm_evaluations"
RESULTS_DIR = BASE_DIR / "01_llm_scoring" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

SOURCE_FILE = DATA_DIR / "llm_3models_284_PERFECT_FINAL.csv"

print(f"{'='*80}")
print(f"LLM 3모델 완전 데이터 분석")
print(f"{'='*80}")
print(f"소스: {SOURCE_FILE}")
print(f"시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*80}\n")

# 데이터 로드
print("[1] 데이터 로드...")
df = pd.read_csv(SOURCE_FILE)
print(f"✓ {len(df)}개 세션, {len(df.columns)}개 컬럼\n")

# 모델 및 카테고리 정의
models = ['gemini', 'anthropic', 'openai']
categories = ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2']
large_cats = ['question', 'answer', 'context', 'overall']

# [2] 3모델 평균 계산
print("[2] 3모델 평균 계산...")
df_avg = df[['session_id']].copy()

# 중분류 평균
for cat in categories:
    cols = [f"{m}_{cat}_total" for m in models]
    if all(c in df.columns for c in cols):
        df_avg[f"avg_{cat}_total"] = df[cols].mean(axis=1)

# 대분류 및 전체 평균
for lcat in large_cats:
    cols = [f"{m}_{lcat}" for m in models]
    if all(c in df.columns for c in cols):
        df_avg[f"avg_{lcat}"] = df[cols].mean(axis=1)

print(f"✓ 평균 데이터프레임 생성: {len(df_avg.columns)-1}개 평균 컬럼\n")

# [3] 기본 통계
print("[3] 기본 통계 계산...")
stats = {}

for model in models:
    model_stats = {}
    
    # 전체 점수
    col = f"{model}_overall"
    if col in df.columns:
        model_stats['overall'] = {
            'mean': float(df[col].mean()),
            'std': float(df[col].std()),
            'median': float(df[col].median())
        }
    
    # 대분류
    for lcat in ['question', 'answer', 'context']:
        col = f"{model}_{lcat}_total"
        if col in df.columns:
            model_stats[lcat] = {
                'mean': float(df[col].mean()),
                'std': float(df[col].std())
            }
    
    # 중분류
    for cat in categories:
        col = f"{model}_{cat}_total"
        if col in df.columns:
            model_stats[cat] = {
                'mean': float(df[col].mean()),
                'std': float(df[col].std())
            }
    
    stats[model] = model_stats

# 3모델 평균 통계
stats['3model_average'] = {}
for col in df_avg.columns:
    if col != 'session_id':
        stats['3model_average'][col.replace('avg_', '')] = {
            'mean': float(df_avg[col].mean()),
            'std': float(df_avg[col].std()),
            'median': float(df_avg[col].median()),
            'min': float(df_avg[col].min()),
            'max': float(df_avg[col].max())
        }

print(f"✓ 통계 계산 완료\n")

# [4] 상관관계 분석
print("[4] 모델 간 상관관계...")
correlations = {}

for lcat in large_cats:
    if lcat == 'overall':
        cols = [f"{m}_overall" for m in models]
    else:
        cols = [f"{m}_{lcat}_total" for m in models]
    
    if all(c in df.columns for c in cols):
        corr = df[cols].corr()
        correlations[lcat] = {
            'gemini_anthropic': float(corr.iloc[0, 1]),
            'gemini_openai': float(corr.iloc[0, 2]),
            'anthropic_openai': float(corr.iloc[1, 2])
        }

print(f"✓ 상관관계 분석 완료\n")

# [5] 결과 저장
print("[5] 결과 저장...")

# 통계
stats_file = RESULTS_DIR / "statistics_perfect.json"
with open(stats_file, 'w', encoding='utf-8') as f:
    json.dump(stats, f, ensure_ascii=False, indent=2)
print(f"✓ {stats_file.name}")

# 상관관계
corr_file = RESULTS_DIR / "correlations_perfect.json"
with open(corr_file, 'w', encoding='utf-8') as f:
    json.dump(correlations, f, ensure_ascii=False, indent=2)
print(f"✓ {corr_file.name}")

# 평균 CSV
avg_file = RESULTS_DIR / "llm_3models_averaged_perfect.csv"
df_avg.to_csv(avg_file, index=False, encoding='utf-8')
print(f"✓ {avg_file.name}")

# 요약
summary = {
    "분석시각": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    "총세션": len(df),
    "전체평균": {
        "gemini": stats['gemini']['overall']['mean'],
        "anthropic": stats['anthropic']['overall']['mean'],
        "openai": stats['openai']['overall']['mean'],
        "3모델평균": stats['3model_average']['overall']['mean']
    },
    "평균상관": {
        pair: np.mean([v[pair] for v in correlations.values()])
        for pair in ['gemini_anthropic', 'gemini_openai', 'anthropic_openai']
    }
}

summary_file = RESULTS_DIR / "summary_perfect.json"
with open(summary_file, 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
print(f"✓ {summary_file.name}\n")

# 최종 출력
print(f"{'='*80}")
print(f"분석 완료!")
print(f"{'='*80}")
print(f"\n주요 결과:")
print(f"  세션 수: {len(df)}")
print(f"\n전체 평균 점수:")
print(f"  • Gemini:    {summary['전체평균']['gemini']:.2f}")
print(f"  • Anthropic: {summary['전체평균']['anthropic']:.2f}")
print(f"  • OpenAI:    {summary['전체평균']['openai']:.2f}")
print(f"  • 3모델평균: {summary['전체평균']['3모델평균']:.2f}")
print(f"\n모델 간 평균 상관:")
for pair, val in summary['평균상관'].items():
    print(f"  • {pair}: {val:.3f}")
print(f"\n결과 위치: {RESULTS_DIR}")
print(f"{'='*80}\n")







