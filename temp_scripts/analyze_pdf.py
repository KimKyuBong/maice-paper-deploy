import pdfplumber
import re
from collections import defaultdict

pdf_path = "myreport.pdf"

# 결과 저장
tables_info = []
figures_info = []
chapters_info = []

print("PDF 분석 시작...")

with pdfplumber.open(pdf_path) as pdf:
    total_pages = len(pdf.pages)
    print(f"총 {total_pages} 페이지")
    
    for page_num, page in enumerate(pdf.pages, 1):
        text = page.extract_text()
        if not text:
            continue
        
        # 표 찾기 - [표Ⅰ-1], [표 1-1], [표 Ⅰ-1] 등 다양한 형식
        table_patterns = [
            r'\[표\s*[IⅠ]\s*-\s*\d+\]',
            r'\[표\s*[IIⅡ]\s*-\s*\d+\]',
            r'\[표\s*[IIIⅢ]\s*-\s*\d+\]',
            r'\[표\s*[IVⅣ]\s*-\s*\d+\]',
            r'\[표\s*[VⅤ]\s*-\s*\d+\]',
            r'\[표\s*[VIⅥ]\s*-\s*\d+\]',
            r'\[표\s*[VIIⅦ]\s*-\s*\d+\]',
            r'\[표\s*[VIIIⅧ]\s*-\s*\d+\]',
            r'\[표\s*\d+\s*-\s*\d+\]',
        ]
        
        for pattern in table_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                clean_match = re.sub(r'\s+', '', match)  # 공백 제거
                if not any(t[0] == clean_match for t in tables_info):
                    tables_info.append((clean_match, page_num))
        
        # 그림 찾기
        figure_patterns = [
            r'\[그림\s*[IⅠ]\s*-\s*\d+\]',
            r'\[그림\s*[IIⅡ]\s*-\s*\d+\]',
            r'\[그림\s*[IIIⅢ]\s*-\s*\d+\]',
            r'\[그림\s*[IVⅣ]\s*-\s*\d+\]',
            r'\[그림\s*[VⅤ]\s*-\s*\d+\]',
            r'\[그림\s*[VIⅥ]\s*-\s*\d+\]',
            r'\[그림\s*[VIIⅦ]\s*-\s*\d+\]',
            r'\[그림\s*[VIIIⅧ]\s*-\s*\d+\]',
            r'\[그림\s*\d+\s*-\s*\d+\]',
        ]
        
        for pattern in figure_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                clean_match = re.sub(r'\s+', '', match)  # 공백 제거
                if not any(f[0] == clean_match for f in figures_info):
                    figures_info.append((clean_match, page_num))
        
        # 챕터 찾기
        chapter_patterns = [
            (r'Ⅰ\s*\.\s*서\s*론', 'Ⅰ. 서론'),
            (r'Ⅱ\s*\.\s*이론적\s*배경', 'Ⅱ. 이론적 배경'),
            (r'Ⅲ\s*\.\s*MAICE\s*교육\s*시스템\s*아키텍처', 'Ⅲ. MAICE 교육 시스템 아키텍처'),
            (r'Ⅲ\s*\.\s*MAICE.*아키텍처', 'Ⅲ. MAICE 시스템'),
            (r'Ⅳ\s*\.\s*MAICE\s*시스템\s*구현', 'Ⅳ. MAICE 시스템 구현'),
            (r'Ⅴ\s*\.\s*베타테스트', 'Ⅴ. 베타테스트'),
            (r'Ⅵ\s*\.\s*연구\s*방법', 'Ⅵ. 연구 방법'),
            (r'Ⅶ\s*\.\s*연구\s*결과', 'Ⅶ. 연구 결과'),
            (r'Ⅷ\s*\.\s*논의\s*및\s*결론', 'Ⅷ. 논의 및 결론'),
        ]
        
        for pattern, name in chapter_patterns:
            if re.search(pattern, text):
                if not any(c[0] == name for c in chapters_info):
                    chapters_info.append((name, page_num))

print("\n=== 챕터 페이지 번호 ===")
for chapter, page in sorted(chapters_info, key=lambda x: x[1]):
    print(f"{chapter}: {page}페이지")

print(f"\n=== 표 목록 (총 {len(tables_info)}개) ===")
for i, (table, page) in enumerate(tables_info[:20], 1):
    print(f"{i}. {table}: {page}페이지")
if len(tables_info) > 20:
    print(f"... 외 {len(tables_info) - 20}개")

print(f"\n=== 그림 목록 (총 {len(figures_info)}개) ===")
for i, (figure, page) in enumerate(figures_info[:20], 1):
    print(f"{i}. {figure}: {page}페이지")
if len(figures_info) > 20:
    print(f"... 외 {len(figures_info) - 20}개")

# 결과를 파일로 저장
with open("pdf_analysis_result.txt", "w", encoding="utf-8") as f:
    f.write("=== 챕터 페이지 번호 ===\n")
    for chapter, page in sorted(chapters_info, key=lambda x: x[1]):
        f.write(f"{chapter}\t{page}\n")
    
    f.write(f"\n=== 표 목록 (총 {len(tables_info)}개) ===\n")
    for table, page in tables_info:
        f.write(f"{table}\t{page}\n")
    
    f.write(f"\n=== 그림 목록 (총 {len(figures_info)}개) ===\n")
    for figure, page in figures_info:
        f.write(f"{figure}\t{page}\n")

print("\n분석 결과를 pdf_analysis_result.txt에 저장했습니다.")

