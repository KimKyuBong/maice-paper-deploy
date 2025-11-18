#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
point.txt를 기반으로 중간고사 점수 + 사분위수를 다시 계산해서
`data/session_data/midterm_scores_with_quartile.csv`를 재생성하는 스크립트.

입력:
- data/session_data/point.txt
    - 컬럼: 서술, 객관, 총합, 계정

출력:
- data/session_data/midterm_scores_with_quartile.csv
    - 컬럼: username, email, essay_score, objective_score, midterm_total, quartile

기능:
1) point.txt를 읽어서 점수/계정 정보를 정규화
2) username (= 이메일 @ 앞부분) 추출
3) midterm_total 기준으로 Q1~Q4 사분위수 계산
4) 기존 midterm_scores_with_quartile.csv는 같은 위치에 덮어씀
   (실제 덮어쓰기 전에 안전하게 backup 파일도 함께 생성)
"""

import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "session_data"
POINT_FILE = DATA_DIR / "point.txt"
OUTPUT_FILE = DATA_DIR / "midterm_scores_with_quartile.csv"
BACKUP_FILE = DATA_DIR / "midterm_scores_with_quartile_backup_from_point.csv"


def load_point_file() -> pd.DataFrame:
    """point.txt를 DataFrame으로 로드하고 컬럼 정리."""
    if not POINT_FILE.exists():
        raise SystemExit(f"point.txt 파일을 찾을 수 없습니다: {POINT_FILE}")

    # 탭/공백 혼합 구분자 처리
    df = pd.read_csv(
        POINT_FILE,
        sep=r"\s+",
        engine="python",
        header=0,
    )

    # 예상 컬럼 이름 매핑
    col_map = {
        "서술": "essay_score",
        "객관": "objective_score",
        "총합": "midterm_total",
        "계정": "email",
    }
    df = df.rename(columns=col_map)

    missing_cols = [c for c in col_map.values() if c not in df.columns]
    if missing_cols:
        raise SystemExit(f"point.txt에서 필요한 컬럼을 찾을 수 없습니다: {missing_cols}")

    # 타입 정리
    for col in ["essay_score", "objective_score", "midterm_total"]:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", ".", regex=False)
            .str.strip()
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["email"] = df["email"].astype(str).str.strip()
    df["username"] = df["email"].str.split("@").str[0]

    return df[["username", "email", "essay_score", "objective_score", "midterm_total"]]


def assign_quartiles(df: pd.DataFrame) -> pd.DataFrame:
    """midterm_total 기준으로 Q1~Q4 사분위수 라벨 부여."""
    if df["midterm_total"].isna().any():
        raise SystemExit("midterm_total에 NaN이 있어 사분위수 계산이 불가능합니다.")

    # pandas qcut으로 4분위수 계산
    df = df.copy()
    df["quartile"] = pd.qcut(
        df["midterm_total"],
        q=4,
        labels=["Q1", "Q2", "Q3", "Q4"],
        duplicates="drop",
    )
    return df


def main():
    print("=" * 80)
    print("point.txt -> midterm_scores_with_quartile.csv 재생성")
    print("=" * 80)

    # 1. point.txt 로드
    df = load_point_file()
    print(f"point.txt 로드 완료: {len(df)}명")

    # 2. 사분위수 계산
    df = assign_quartiles(df)
    print("사분위수(Q1~Q4) 계산 완료")

    # 3. 백업 파일 저장 (기존 CSV가 있을 경우)
    if OUTPUT_FILE.exists():
        print(f"기존 파일 백업 생성: {BACKUP_FILE.name}")
        OUTPUT_FILE.replace(BACKUP_FILE)

    # 4. 최종 CSV 저장
    df_out = df[["username", "email", "essay_score", "objective_score", "midterm_total", "quartile"]]
    df_out.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    print(f"새로운 중간고사+사분위수 CSV 저장: {OUTPUT_FILE.relative_to(BASE_DIR)}")
    print("=" * 80)


if __name__ == "__main__":
    main()


