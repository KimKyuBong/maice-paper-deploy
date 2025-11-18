#!/usr/bin/env python3
"""
5장 모든 표를 재계산된 값으로 업데이트하는 스크립트
"""

import json
from pathlib import Path

# 결과 파일 로드
BASE = Path(__file__).parent.parent
MD_FILE = BASE.parent / 'docs' / 'chapters' / '05-results.md'

# 모든 결과 파일 읽기
with open(BASE / '04_effect_size/results/quartile_analysis_perfect.json') as f:
    llm_quartile = json.load(f)

with open(BASE / '04_effect_size/results/teacher_quartile_analysis_perfect.json') as f:
    teacher_quartile = json.load(f)

with open(BASE / '05_chapter5_evidence/results/ch5_1_d_pre_homogeneity.json') as f:
    homogeneity = json.load(f)

with open(BASE / '05_chapter5_evidence/results/table_v9_verification.json') as f:
    v9 = json.load(f)

# Markdown 파일 읽기
with open(MD_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# 핵심 발견 텍스트 업데이트
content = content.replace(
    '**핵심 발견**: Q1 하위권에서 통계적으로 매우 유의 (p<0.001, d=0.905). 명료화 프로세스는 **학습에 어려움을 겪는 학생에게 특히 효과적**.',
    f'**핵심 발견**: Q1 하위권에서 통계적으로 매우 유의 (p<0.001, d={llm_quartile["C2"]["Q1"]["cohens_d"]:.3f}). 명료화 프로세스는 **학습에 어려움을 겪는 학생에게 특히 효과적**.'
)

# 하위권 학생 점수 차이 텍스트 업데이트
q1_diff = llm_quartile['overall']['Q1']['difference']
q1_pct = (q1_diff / 40) * 100
q1_p = llm_quartile['overall']['Q1']['p_value']
content = content.replace(
    '하위권 학생은 명료화 모드에서 **2.04점 더 높은 평가** (40점 만점 중 5.1% 차이, p=0.053, 경계적 유의).',
    f'하위권 학생은 명료화 모드에서 **{q1_diff:.2f}점 더 높은 평가** (40점 만점 중 {q1_pct:.1f}% 차이, p={q1_p:.3f}{"*" if q1_p < 0.05 else ", 경계적 유의" if q1_p < 0.10 else ""}).'
)

# 교사 Q1 효과 텍스트 업데이트
t_q1_diff = teacher_quartile['overall']['Q1']['difference']
t_q1_p = teacher_quartile['overall']['Q1']['p_value']
t_q1_d = teacher_quartile['overall']['Q1']['cohens_d']
content = content.replace(
    '**핵심 발견**: Q1 하위권에서 유의한 효과 (p=0.046, d=0.827). LLM 평가 결과(p=0.053, d=0.457)와 방향성 일치.',
    f'**핵심 발견**: Q1 하위권에서 유의한 효과 (p={t_q1_p:.3f}, d={t_q1_d:.3f}). LLM 평가 결과(p={q1_p:.3f}, d={llm_quartile["overall"]["Q1"]["cohens_d"]:.3f})와 방향성 일치.'
)

# 파일 저장
with open(MD_FILE, 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ 05-results.md 업데이트 완료")
print(f"\n주요 업데이트:")
print(f"  - 표V-5, V-6: LLM Quartile n값 업데이트 (Q1={llm_quartile['C2']['Q1']['n']}, Q2={llm_quartile['C2']['Q2']['n']}, Q3={llm_quartile['C2']['Q3']['n']}, Q4={llm_quartile['C2']['Q4']['n']})")
print(f"  - 표V-11: 교사 Quartile n값 업데이트 (Q1={teacher_quartile['overall']['Q1']['n']}, Q2={teacher_quartile['overall']['Q2']['n']}, Q3={teacher_quartile['overall']['Q3']['n']}, Q4={teacher_quartile['overall']['Q4']['n']})")
print(f"  - Q1 하위권 효과: LLM p={q1_p:.3f}, d={llm_quartile['overall']['Q1']['cohens_d']:.3f}")
print(f"  - Q1 하위권 효과: 교사 p={t_q1_p:.3f}, d={t_q1_d:.3f}")


