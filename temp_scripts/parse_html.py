import re
from pathlib import Path

html_file = Path("htmldocs/docs.html")
content = html_file.read_text(encoding='utf-8')

# HTML에서 표와 그림 찾기
table_pattern = r'\[표[^\]]+\]'
figure_pattern = r'\[그림[^\]]+\]'

tables = re.findall(table_pattern, content)
figures = re.findall(figure_pattern, content)

print("=== 표 목록 ===")
for i, table in enumerate(tables[:10], 1):
    print(f"{i}. {table}")

print(f"\n총 {len(tables)}개의 표 발견")

print("\n=== 그림 목록 ===")
for i, figure in enumerate(figures[:10], 1):
    print(f"{i}. {figure}")

print(f"\n총 {len(figures)}개의 그림 발견")

# 챕터 제목 찾기
chapter_patterns = [
    r'Ⅰ\.\s*서\s*론',
    r'Ⅱ\.\s*이론적\s*배경',
    r'Ⅲ\.\s*MAICE',
    r'Ⅳ\.\s*MAICE\s*시스템\s*구현',
    r'Ⅴ\.\s*베타테스트',
    r'Ⅵ\.\s*연구\s*방법',
    r'Ⅶ\.\s*연구\s*결과',
    r'Ⅷ\.\s*논의\s*및\s*결론',
]

print("\n=== 챕터 검색 ===")
for pattern in chapter_patterns:
    matches = re.findall(pattern, content)
    if matches:
        print(f"발견: {pattern} -> {matches[0]}")

