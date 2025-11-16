#!/usr/bin/env python3
"""
LLM 채점점수 처리 및 검증

논문 5장 표Ⅴ-4에서 사용된 LLM 3개 모델 평균 처리 방법을 검증합니다.

⚠️ 중요: 최종 생성된 CSV 파일만 사용합니다.
- 입력: llm_3models_284_PERFECT_FINAL.csv (3개 모델 채점 결과)
- 출력: llm_3models_averaged_perfect.csv (3개 모델 평균)

근거:
- 논문 5장 2절 나항 "LLM 평가 결과 (N=284)"
- 표Ⅴ-4: 세부 항목별 모드 비교
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

print("="*80)
print("LLM 채점점수 처리 및 검증")
print("="*80)
print()
print("⚠️  최종 CSV 파일만 사용합니다: llm_3models_284_PERFECT_FINAL.csv")
print()

# 데이터 경로 설정
BASE_PATH = Path(__file__).parent.parent / "data"
OUTPUT_PATH = Path(__file__).parent / "results"
OUTPUT_PATH.mkdir(exist_ok=True)

# ============================================================================
# 1. 최종 CSV 파일 로드
# ============================================================================

print("1. 최종 CSV 파일 로드")
print("-" * 80)

SOURCE_FILE = BASE_PATH / "llm_evaluations" / "llm_3models_284_PERFECT_FINAL.csv"

if not SOURCE_FILE.exists():
    print(f"❌ 파일이 없습니다: {SOURCE_FILE}")
    print("최종 생성된 CSV 파일이 필요합니다: llm_3models_284_PERFECT_FINAL.csv")
    sys.exit(1)

df = pd.read_csv(SOURCE_FILE)
print(f"✓ 파일 로드 완료: {len(df)}개 세션, {len(df.columns)}개 컬럼")
print()

# ============================================================================
# 2. 3개 모델 평균 계산
# ============================================================================

print("2. 3개 모델 평균 계산")
print("-" * 80)

models = ['gemini', 'anthropic', 'openai']
categories = ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2']
large_cats = ['question', 'answer', 'context', 'overall']

# 평균 데이터프레임 생성
df_avg = df[['session_id']].copy()

# 중분류 평균 (A1, A2, ..., C2)
for cat in categories:
    cols = [f"{m}_{cat}_total" for m in models]
    if all(c in df.columns for c in cols):
        df_avg[f"avg_{cat}_total"] = df[cols].mean(axis=1)
        print(f"✓ {cat} 평균 계산 완료")

# 대분류 및 전체 평균
for lcat in large_cats:
    cols = [f"{m}_{lcat}" for m in models]
    if all(c in df.columns for c in cols):
        df_avg[f"avg_{lcat}"] = df[cols].mean(axis=1)
        print(f"✓ {lcat} 평균 계산 완료")

print(f"\n✓ 평균 데이터프레임 생성: {len(df_avg.columns)-1}개 평균 컬럼")
print()

# ============================================================================
# 3. 결과 저장
# ============================================================================

print("3. 결과 저장")
print("-" * 80)

output_file = OUTPUT_PATH / "llm_3models_averaged_perfect.csv"
df_avg.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"✓ 저장 완료: {output_file}")
print()

# ============================================================================
# 4. 기본 통계 출력
# ============================================================================

print("4. 기본 통계")
print("-" * 80)

if 'avg_overall' in df_avg.columns:
    print(f"전체 평균 점수: {df_avg['avg_overall'].mean():.2f} (SD={df_avg['avg_overall'].std():.2f})")
    print(f"세션 수: {len(df_avg)}개")
    print()

print("="*80)
print("처리 완료!")
print("="*80)
print()
print("📁 출력 파일:")
print(f"   - {output_file}")
print()
print("⚠️  참고: 이 스크립트는 최종 CSV 파일만 사용합니다.")
print("   원본 JSONL 파일은 사용하지 않습니다.")
