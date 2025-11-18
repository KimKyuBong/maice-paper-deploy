#!/usr/bin/env python3
"""
교사 평가 매칭 데이터 생성

목적: inter_rater_reliability.py가 필요로 하는 teacher_matched_scores.csv 생성
- 평가자 96, 97만 사용
- 같은 세션에 대한 두 평가를 매칭
"""

import json
import pandas as pd
from pathlib import Path

print("="*80)
print("교사 평가 매칭 데이터 생성")
print("="*80)
print()

BASE_DIR = Path(__file__).parent.parent
INPUT_FILE = BASE_DIR / "data" / "teacher_evaluations" / "latest_evaluations.json"
OUTPUT_DIR = Path(__file__).parent / "results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 데이터 로드
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"[1] 데이터 로드: {len(data)}개 레코드")

# 평가자 96, 97만 필터링
filtered_data = [
    item for item in data
    if item.get('evaluation_status') == 'completed'
    and item.get('overall_score') is not None
    and item.get('evaluated_by') in [96, 97]
]

print(f"[2] 평가자 96, 97 필터링: {len(filtered_data)}개 레코드")

# DataFrame 변환
df = pd.DataFrame(filtered_data)

# 필요한 컬럼만 선택
score_cols = [
    'id',
    'conversation_session_id',
    'evaluated_by',
    'student_id',
    'question_professionalism_score',
    'question_structuring_score',
    'question_context_application_score',
    'answer_customization_score',
    'answer_systematicity_score',
    'answer_expandability_score',
    'context_dialogue_coherence_score',
    'context_learning_support_score',
    'overall_score'
]

# 존재하는 컬럼만 선택
available_cols = [col for col in score_cols if col in df.columns]
df_filtered = df[available_cols].copy()

# 점수 계산
if 'question_professionalism_score' in df_filtered.columns:
    df_filtered['question_total_score'] = (
        df_filtered['question_professionalism_score'].fillna(0) +
        df_filtered['question_structuring_score'].fillna(0) +
        df_filtered['question_context_application_score'].fillna(0)
    )

if 'answer_customization_score' in df_filtered.columns:
    df_filtered['response_total_score'] = (
        df_filtered['answer_customization_score'].fillna(0) +
        df_filtered['answer_systematicity_score'].fillna(0) +
        df_filtered['answer_expandability_score'].fillna(0)
    )

if 'context_dialogue_coherence_score' in df_filtered.columns:
    df_filtered['context_total_score'] = (
        df_filtered['context_dialogue_coherence_score'].fillna(0) +
        df_filtered['context_learning_support_score'].fillna(0)
    )

# 저장
output_file = OUTPUT_DIR / "teacher_matched_scores.csv"
df_filtered.to_csv(output_file, index=False, encoding='utf-8')

print(f"[3] 매칭 데이터 저장: {output_file}")
print(f"    - 레코드 수: {len(df_filtered)}개")
print(f"    - 평가자 96: {len(df_filtered[df_filtered['evaluated_by'] == 96])}개")
print(f"    - 평가자 97: {len(df_filtered[df_filtered['evaluated_by'] == 97])}개")
print()

print("✓ 완료!")
print("="*80)


