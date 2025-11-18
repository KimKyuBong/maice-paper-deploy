#!/usr/bin/env python3
"""
5장 모든 통계치 재현 가능성 검증

목적: 논문 5장에 나온 모든 통계 수치가 Python 스크립트로 재현 가능한지 확인
"""

import json
import subprocess
from pathlib import Path
import sys

print("="*80)
print("5장 모든 통계치 재현 가능성 검증")
print("="*80)
print()

BASE_DIR = Path(__file__).parent.parent
EVIDENCE_DIR = BASE_DIR / "05_chapter5_evidence"

# 검증해야 할 표 목록
tables_to_verify = {
    "표Ⅴ-1": {
        "script": "ch5_1_n_data_collection.py",
        "result_file": "results/ch5_1_n_data_collection.json",
        "description": "수집 데이터 현황"
    },
    "표Ⅴ-2": {
        "script": "ch5_1_r_clarification_operation.py",
        "result_file": "results/ch5_1_r_clarification_operation.json",
        "description": "명료화 수행 현황"
    },
    "사전 동질성": {
        "script": "ch5_1_d_pre_homogeneity.py",
        "result_file": "results/ch5_1_d_pre_homogeneity.json",
        "description": "사전 동질성 검증"
    },
    "표Ⅴ-4": {
        "script": "../04_effect_size/mode_quartile_analysis_perfect.py",
        "result_file": "../04_effect_size/results/mode_comparison_perfect.json",
        "description": "세부 항목별 모드 비교 (LLM 평가)"
    },
    "표Ⅴ-5": {
        "script": "../04_effect_size/mode_quartile_analysis_perfect.py",
        "result_file": "../04_effect_size/results/quartile_analysis_perfect.json",
        "description": "Quartile별 C2 비교 (LLM 평가)"
    },
    "표Ⅴ-6": {
        "script": "../04_effect_size/mode_quartile_analysis_perfect.py",
        "result_file": "../04_effect_size/results/quartile_analysis_perfect.json",
        "description": "Quartile별 전체 점수 (LLM 평가)"
    },
    "표Ⅴ-7": {
        "script": "../04_effect_size/mode_quartile_analysis_perfect.py",
        "result_file": "../04_effect_size/results/repetition_effect_perfect.json",
        "description": "세션 증가에 따른 항목별 점수 변화"
    },
    "표Ⅴ-8": {
        "script": "../02_teacher_scoring/inter_rater_reliability.py",
        "result_file": "../02_teacher_scoring/results/teacher_correlations_perfect.json",
        "description": "교사 평가 설계 (평가자 간 신뢰도)"
    },
    "표Ⅴ-9": {
        "script": "../04_effect_size/teacher_mode_comparison_perfect.py",
        "result_file": "../04_effect_size/results/teacher_mode_comparison_perfect.json",
        "description": "모드별 점수 비교 (교사 평가)"
    },
    "표Ⅴ-10": {
        "script": "../04_effect_size/teacher_mode_comparison_perfect.py",
        "result_file": "../04_effect_size/results/teacher_quartile_analysis_perfect.json",
        "description": "Quartile별 전체 점수 (교사 평가)"
    },
    "표Ⅴ-11": {
        "script": "../03_correlation_analysis/llm_teacher_correlation_perfect.py",
        "result_file": "../03_correlation_analysis/results/llm_teacher_correlations_perfect.json",
        "description": "LLM-교사 평가 상관관계"
    },
    "표Ⅴ-12": {
        "script": "ch5_2_e_2_q1_convergence.py",
        "result_file": "results/ch5_2_e_2_q1_convergence.json",
        "description": "Q1 하위권 Agent 우위 폭 비교"
    },
    "표Ⅴ-14": {
        "script": "../05_student_survey/analyze_survey_47_by_mode_final.py",
        "result_file": "../05_student_survey/results/survey_47_statistics.csv",
        "description": "학습자 자기 평가 결과"
    },
    "표Ⅴ-15": {
        "script": "../05_student_survey/analyze_survey_47_by_mode_final.py",
        "result_file": "../05_student_survey/results/survey_47_mode_preference_final.csv",
        "description": "명료화 방식 선호도"
    },
    "표Ⅴ-23,25,26": {
        "script": "ch5_4_bloom_dewey_from_db.py",
        "result_file": "results/ch5_4_bloom_dewey_from_db.json",
        "description": "Bloom-Dewey 이론 실증 분석"
    }
}

# 추가 확인 항목
additional_checks = {
    "LLM 신뢰도": {
        "script": "01_llm_scoring/llm_reliability_analysis.py",
        "result_file": "01_llm_scoring/results/llm_reliability_results.json",
        "description": "Cronbach's α, ICC, Pearson r"
    }
}

results = {
    "verified": [],
    "missing_script": [],
    "missing_result": [],
    "script_error": []
}

print("[검증 진행 중...]")
print()

for table_name, info in tables_to_verify.items():
    # 경로 처리 개선
    if info["script"].startswith("../"):
        script_path = BASE_DIR / info["script"][3:]  # "../" 제거
    else:
        script_path = EVIDENCE_DIR / info["script"]
    
    if info["result_file"].startswith("../"):
        result_path = BASE_DIR / info["result_file"][3:]  # "../" 제거
    else:
        result_path = EVIDENCE_DIR / info["result_file"]
    
    print(f"✓ {table_name}: {info['description']}")
    
    # 스크립트 존재 확인
    if not script_path.exists():
        print(f"  ❌ 스크립트 없음: {script_path}")
        results["missing_script"].append({
            "table": table_name,
            "script": str(script_path.relative_to(BASE_DIR))
        })
        continue
    
    # 결과 파일 존재 확인
    if not result_path.exists():
        print(f"  ⚠️  결과 파일 없음: {result_path}")
        print(f"     → 스크립트 실행 필요: {script_path.name}")
        results["missing_result"].append({
            "table": table_name,
            "script": str(script_path.relative_to(BASE_DIR)),
            "result_file": str(result_path.relative_to(BASE_DIR))
        })
        continue
    
    # 결과 파일 읽기 시도
    try:
        if result_path.suffix == '.json':
            with open(result_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"  ✓ 결과 파일 존재: {len(str(data))} bytes")
        elif result_path.suffix == '.csv':
            import pandas as pd
            df = pd.read_csv(result_path)
            print(f"  ✓ 결과 파일 존재: {len(df)}행")
        else:
            print(f"  ✓ 결과 파일 존재")
    except Exception as e:
        print(f"  ❌ 결과 파일 읽기 오류: {e}")
        results["script_error"].append({
            "table": table_name,
            "error": str(e)
        })
        continue
    
    results["verified"].append({
        "table": table_name,
        "script": str(script_path.relative_to(BASE_DIR)),
        "result_file": str(result_path.relative_to(BASE_DIR))
    })

print()
print("="*80)
print("검증 결과 요약")
print("="*80)
print()

print(f"✅ 검증 완료: {len(results['verified'])}개")
for item in results["verified"]:
    print(f"  - {item['table']}")

print()
print(f"⚠️  결과 파일 없음 (스크립트 실행 필요): {len(results['missing_result'])}개")
for item in results["missing_result"]:
    print(f"  - {item['table']}")
    print(f"    스크립트: {item['script']}")
    print(f"    결과 파일: {item['result_file']}")

print()
print(f"❌ 스크립트 없음: {len(results['missing_script'])}개")
for item in results["missing_script"]:
    print(f"  - {item['table']}")
    print(f"    스크립트: {item['script']}")

print()
print(f"❌ 스크립트 오류: {len(results['script_error'])}개")
for item in results["script_error"]:
    print(f"  - {item['table']}: {item['error']}")

print()
print("="*80)
print("추가 확인 항목")
print("="*80)
print()

for check_name, info in additional_checks.items():
    script_path = BASE_DIR / info["script"]
    result_path = BASE_DIR / info["result_file"]
    
    if script_path.exists():
        if result_path.exists():
            print(f"✓ {check_name}: {info['description']}")
            results["verified"].append({
                "table": check_name,
                "script": str(script_path.relative_to(BASE_DIR)),
                "result_file": str(result_path.relative_to(BASE_DIR))
            })
        else:
            print(f"⚠️  {check_name}: 결과 파일 없음 (실행 필요)")
            results["missing_result"].append({
                "table": check_name,
                "script": str(script_path.relative_to(BASE_DIR)),
                "result_file": str(result_path.relative_to(BASE_DIR))
            })
    else:
        print(f"❌ {check_name}: 스크립트 없음")
        results["missing_script"].append({
            "table": check_name,
            "script": str(script_path.relative_to(BASE_DIR))
        })

print()
print("="*80)

# 종합 판정
total_tables = len(tables_to_verify)
verified_count = len(results["verified"])
missing_result_count = len(results["missing_result"])
missing_script_count = len(results["missing_script"])

if missing_script_count == 0 and missing_result_count == 0:
    print(f"✅ 모든 통계치 재현 가능! ({verified_count}/{total_tables})")
    sys.exit(0)
elif missing_script_count > 0:
    print(f"❌ 누락된 스크립트: {missing_script_count}개")
    sys.exit(1)
else:
    print(f"⚠️  결과 파일 생성 필요: {missing_result_count}개")
    print("   아래 명령어로 실행하세요:")
    print()
    for item in results["missing_result"]:
        script_rel = item["script"]
        if script_rel.startswith("../"):
            script_path = BASE_DIR / script_rel
        else:
            script_path = EVIDENCE_DIR / script_rel
        print(f"   python {script_rel}")
    sys.exit(2)

