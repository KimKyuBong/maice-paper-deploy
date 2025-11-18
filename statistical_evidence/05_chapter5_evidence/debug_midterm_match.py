#!/usr/bin/env python3
"""
중간고사 점수 매칭이 안 된 세션을 정확히 확인하는 디버그 스크립트.

1) 전체 284개 세션 중 midterm_scores_with_quartile.csv와 매칭되지 않은 세션
2) 교사 표본 100개 세션 중 중간고사 점수가 없는 세션
   - 어떤 session_id / username 인지 그대로 출력
"""

import pandas as pd
from pathlib import Path
import json

BASE = Path(__file__).parent.parent.parent
SESSION_CSV = BASE / "statistical_evidence" / "data" / "session_data" / "full_sessions_with_scores.csv"
MIDTERM_CSV = BASE / "statistical_evidence" / "data" / "session_data" / "midterm_scores_with_quartile.csv"
TEACHER_JSON = BASE / "statistical_evidence" / "data" / "teacher_evaluations" / "latest_evaluations.json"


def main():
    print("=" * 80)
    print("중간고사 매칭 디버그: 어떤 세션에 점수가 비어 있는가?")
    print("=" * 80)

    # 1. 세션 전체 로드
    df_sessions = pd.read_csv(SESSION_CSV)
    print(f"\n전체 세션 수 (CSV): {len(df_sessions)}개")

    # username 정규화
    df_sessions["username_clean"] = (
        df_sessions["username"]
        .astype(str)
        .str.replace("@bssm.hs.kr", "", regex=False)
        .str.replace(".", "", regex=False)
    )

    # 2. 중간고사 점수 로드 (username은 이미 24.010@bssm.hs.kr 형태로 저장됨)
    df_mid = pd.read_csv(MIDTERM_CSV)
    print(f"중간고사 점수 행 수 (CSV): {len(df_mid)}명")

    df_mid["username_clean"] = (
        df_mid["username"]
        .astype(str)
        .str.replace("@bssm.hs.kr", "", regex=False)
        .str.replace(".", "", regex=False)
    )

    # midterm_total 컬럼 확인
    if "midterm_total" not in df_mid.columns:
        raise SystemExit("midterm_scores_with_quartile.csv 에 midterm_total 컬럼이 없습니다.")

    # 3. 세션 전체와 중간고사 병합
    merged = df_sessions.merge(
        df_mid[["username_clean", "midterm_total"]],
        on="username_clean",
        how="left",
    )

    no_mid = merged[merged["midterm_total"].isna()].copy()
    print(f"\n▶ 전체 284개 세션 중 중간고사 점수가 매칭 안 된 세션 수: {len(no_mid)}개")

    if len(no_mid) > 0:
        print("\n[중간고사 점수 없는 세션 목록 (전체 284개 기준)]")
        print(
            no_mid[["session_id", "username", "mode", "created_at"]]
            .sort_values(["username", "session_id"])
            .to_string(index=False)
        )

    # 4. 교사 표본 100개 세션 ID 로드
    with open(TEACHER_JSON, "r", encoding="utf-8") as f:
        teacher_data = json.load(f)

    teacher_sessions = set()
    if isinstance(teacher_data, list):
        for r in teacher_data:
            if r.get("evaluated_by") in [96, 97]:
                sid = r.get("conversation_session_id")
                if sid is not None:
                    teacher_sessions.add(sid)
    else:
        for r in teacher_data.get("results", []):
            if r.get("evaluated_by") in [96, 97] or r.get("evaluator_id") in [96, 97]:
                sid = r.get("conversation_session_id") or r.get("session_id")
                if sid is not None:
                    teacher_sessions.add(sid)

    print(f"\n교사 표본 세션 수 (JSON 기준 고유 session_id): {len(teacher_sessions)}개")

    sample = merged[merged["session_id"].isin(teacher_sessions)].copy()
    print(f"세션 CSV와 교사 JSON 기준으로 매칭된 표본 세션 수: {len(sample)}개")

    no_mid_sample = sample[sample["midterm_total"].isna()].copy()
    print(f"\n▶ 교사 표본 100개 중 중간고사 점수가 없는 세션 수: {len(no_mid_sample)}개")

    if len(no_mid_sample) > 0:
        print("\n[교사 표본 중 중간고사 점수 없는 세션 목록]")
        print(
            no_mid_sample[["session_id", "username", "mode", "created_at"]]
            .sort_values(["username", "session_id"])
            .to_string(index=False)
        )


if __name__ == "__main__":
    main()


