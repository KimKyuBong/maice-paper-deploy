#!/usr/bin/env python3
"""
교사 채점점수 처리 및 검증

논문 5장 2절 다항 "교사 평가 (N=100)"에서 사용된 교사 평가 데이터를 처리합니다.

주요 기능:
1. 교사 2명(ID: 96, 97) 평가 데이터 로드
2. 동일 세션 대응 확인
3. 평가자별 기술통계
4. 영역별 점수 계산

근거:
- 논문 5장 2절 다항(1) "평가 설계"
- 표Ⅴ-8: 교사 평가 설계
- 표Ⅴ-9: 모드별 점수 비교
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
import sys

print("="*80)
print("교사 채점점수 처리 및 검증")
print("="*80)
print()

# 경로 설정
BASE_PATH = Path(__file__).parent.parent / "data"
OUTPUT_PATH = Path(__file__).parent / "results"
OUTPUT_PATH.mkdir(exist_ok=True)

# ============================================================================
# 1. 데이터 로드
# ============================================================================

print("1. 교사 평가 데이터 로드")
print("-" * 80)

# 교사 평가 데이터 파일
teacher_file = BASE_PATH / "teacher_evaluations" / "latest_evaluations.json"

if not teacher_file.exists():
    print(f"⚠️  파일이 없습니다: {teacher_file}")
    sys.exit(1)

with open(teacher_file, 'r', encoding='utf-8') as f:
    teacher_data = json.load(f)

df = pd.DataFrame(teacher_data)

print(f"✓ 총 평가 레코드: {len(df)}개")
print()

# 평가자 확인
evaluators = sorted(df['evaluated_by'].unique())
print(f"평가자: {evaluators}")

for evaluator in evaluators:
    count = len(df[df['evaluated_by'] == evaluator])
    sessions = df[df['evaluated_by'] == evaluator]['conversation_session_id'].nunique()
    print(f"  교사 {evaluator}: {count}개 레코드, {sessions}개 세션")

print()

# ============================================================================
# 2. 교사 96, 97만 필터링
# ============================================================================

print("2. 교사 96, 97 데이터 필터링")
print("-" * 80)

# 논문에서는 교사 96, 97만 사용
df_filtered = df[df['evaluated_by'].isin([96, 97])].copy()

print(f"필터링 후: {len(df_filtered)}개 레코드")

evaluators_96_97 = sorted(df_filtered['evaluated_by'].unique())
for evaluator in evaluators_96_97:
    count = len(df_filtered[df_filtered['evaluated_by'] == evaluator])
    sessions = df_filtered[df_filtered['evaluated_by'] == evaluator]['conversation_session_id'].nunique()
    print(f"  교사 {evaluator}: {count}개 레코드, {sessions}개 세션")

print()

# ============================================================================
# 3. 동일 세션 대응 확인 (완전한 대응 설계)
# ============================================================================

print("3. 동일 세션 대응 확인")
print("-" * 80)

sessions_96 = set(df_filtered[df_filtered['evaluated_by'] == 96]['conversation_session_id'])
sessions_97 = set(df_filtered[df_filtered['evaluated_by'] == 97]['conversation_session_id'])

common_sessions = sessions_96 & sessions_97

print(f"교사 96 평가 세션: {len(sessions_96)}개")
print(f"교사 97 평가 세션: {len(sessions_97)}개")
print(f"공통 평가 세션: {len(common_sessions)}개")
print()

if len(common_sessions) == len(sessions_96) == len(sessions_97):
    print("✓ 완전한 대응 설계 확인 (동일 세션 독립 평가)")
else:
    print("⚠️  대응 설계 불완전: 일부 세션이 한 명에게만 평가됨")

print()

# 공통 세션만 필터링
df_matched = df_filtered[df_filtered['conversation_session_id'].isin(common_sessions)].copy()

print(f"대응 설계 데이터: {len(df_matched)}개 레코드 ({len(common_sessions)} × 2)")
print()

# ============================================================================
# 4. 점수 항목 정의 및 계산
# ============================================================================

print("4. 영역별 점수 계산")
print("-" * 80)

# 루브릭 항목 정의
score_columns = {
    '질문': ['question_professionalism_score', 'question_structuring_score', 
              'question_context_application_score', 'question_total_score'],
    '응답': ['answer_customization_score', 'answer_systematicity_score',
              'answer_expandability_score', 'response_total_score'],
    '맥락': ['context_dialogue_coherence_score', 'context_learning_support_score',
              'context_total_score'],
    '종합': ['overall_score']
}

# 숫자 변환
numeric_columns = [
    'question_professionalism_score',
    'question_structuring_score',
    'question_context_application_score',
    'question_total_score',
    'answer_customization_score',
    'answer_systematicity_score',
    'answer_expandability_score',
    'response_total_score',
    'context_dialogue_coherence_score',
    'context_learning_support_score',
    'context_total_score',
    'overall_score'
]

for col in numeric_columns:
    df_matched[col] = pd.to_numeric(df_matched[col], errors='coerce')

# 기술통계 출력
for area, cols in score_columns.items():
    if area == '종합':
        col = 'overall_score'
    else:
        col = [c for c in cols if '_total_' in c][0]
    
    print(f"\n【{area} 영역】")
    for evaluator in [96, 97]:
        data = df_matched[df_matched['evaluated_by'] == evaluator][col]
        print(f"  교사 {evaluator}: M={data.mean():.2f}, SD={data.std():.2f}, "
              f"Min={data.min():.0f}, Max={data.max():.0f}")

print()

# ============================================================================
# 5. 평균 점수 계산 (2명 평균)
# ============================================================================

print("5. 교사 2명 평균 계산")
print("-" * 80)

# 세션별로 교사 2명 평균 계산
averaged_data = []

for session_id in common_sessions:
    session_data = df_matched[df_matched['conversation_session_id'] == session_id]
    
    if len(session_data) != 2:
        continue
    
    # 2명의 점수 평균
    avg_record = {'conversation_session_id': session_id}
    
    for col in numeric_columns:
        scores = session_data[col].values
        avg_record[col] = np.mean(scores)
    
    averaged_data.append(avg_record)

df_averaged = pd.DataFrame(averaged_data)

print(f"✓ {len(df_averaged)}개 세션에 대해 교사 2명 평균 계산 완료")
print()

# 평균 점수 기술통계
print("교사 2명 평균 점수 기술통계:")
print("-" * 80)

for area, cols in score_columns.items():
    if area == '종합':
        col = 'overall_score'
    else:
        col = [c for c in cols if '_total_' in c][0]
    
    data = df_averaged[col]
    print(f"{area:6s}: M={data.mean():.2f}, SD={data.std():.2f}, "
          f"Min={data.min():.2f}, Max={data.max():.2f}")

print()

# ============================================================================
# 6. 결과 저장
# ============================================================================

print("6. 결과 저장")
print("-" * 80)

# 원본 매칭 데이터 (교사별)
matched_csv = OUTPUT_PATH / "teacher_matched_scores.csv"
df_matched.to_csv(matched_csv, index=False, encoding='utf-8-sig')
print(f"✓ 교사별 매칭 점수 저장: {matched_csv}")

# 2명 평균 데이터
averaged_csv = OUTPUT_PATH / "teacher_averaged_scores.csv"
df_averaged.to_csv(averaged_csv, index=False, encoding='utf-8-sig')
print(f"✓ 교사 2명 평균 점수 저장: {averaged_csv}")

# 요약 통계
summary = {
    'n_teachers': 2,
    'teacher_ids': [96, 97],
    'n_common_sessions': len(common_sessions),
    'n_total_records': len(df_matched),
    'score_categories': list(score_columns.keys()),
    'descriptive_stats': {
        area: {
            'mean': float(df_averaged[[c for c in cols if '_total_' in c or c == 'overall_score'][0]].mean()),
            'std': float(df_averaged[[c for c in cols if '_total_' in c or c == 'overall_score'][0]].std()),
            'min': float(df_averaged[[c for c in cols if '_total_' in c or c == 'overall_score'][0]].min()),
            'max': float(df_averaged[[c for c in cols if '_total_' in c or c == 'overall_score'][0]].max())
        }
        for area, cols in score_columns.items()
    }
}

summary_json = OUTPUT_PATH / "teacher_score_summary.json"
with open(summary_json, 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
print(f"✓ 요약 통계 저장: {summary_json}")

print()
print("="*80)
print("교사 채점점수 처리 완료!")
print("="*80)
print()
print(f"📊 최종 데이터셋: N={len(common_sessions)} (교사 2명 완전 대응)")
print(f"👥 평가자: 교사 96, 97 (외부 수학 교사)")
print(f"📋 평가 영역: 4개 (질문, 응답, 맥락, 종합)")
print()

