"""
표 셀의 정확한 스타일 분석 (borderFillIDRef 등)
"""
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("표 셀 스타일 상세 분석")
print("="*80)

with open('hwp/analyze_original/Contents/section2.xml', 'r', encoding='utf-8') as f:
    content = f.read()

# 첫 번째 표 추출
table_pattern = r'<hp:tbl id="\d+".*?</hp:tbl>'
tables = re.findall(table_pattern, content, re.DOTALL)

if tables:
    first_table = tables[0]
    
    print(f"\n첫 번째 표 분석:")
    print("="*80)
    
    # 행들 추출
    rows = re.findall(r'<hp:tr>(.*?)</hp:tr>', first_table, re.DOTALL)
    
    print(f"총 {len(rows)}개 행\n")
    
    for row_idx, row_xml in enumerate(rows):
        print(f"\n--- 행 {row_idx + 1} ---")
        
        # 셀들 추출
        cells = re.findall(r'<hp:tc[^>]*>(.*?)</hp:tc>', row_xml, re.DOTALL)
        
        for cell_idx, cell_xml in enumerate(cells[:3]):  # 처음 3개 셀만
            # borderFillIDRef 추출
            border_fill = re.search(r'borderFillIDRef="(\d+)"', cell_xml)
            
            # header 속성
            header_attr = re.search(r'header="(\d+)"', cell_xml)
            
            # 텍스트
            texts = re.findall(r'<hp:t>(.*?)</hp:t>', cell_xml)
            text = ''.join(texts)[:40]
            
            print(f"  셀 {cell_idx + 1}:")
            print(f"    borderFillIDRef: {border_fill.group(1) if border_fill else 'N/A'}")
            print(f"    header: {header_attr.group(1) if header_attr else 'N/A'}")
            print(f"    텍스트: {text}")
        
        if row_idx >= 3:  # 처음 4개 행만
            break

# borderFill 정의 확인 (header.xml)
print("\n\n" + "="*80)
print("borderFill 정의 확인 (header.xml)")
print("="*80)

with open('hwp/analyze_original/Contents/header.xml', 'r', encoding='utf-8') as f:
    header = f.read()

# borderFill 태그들
border_fills = re.findall(r'<hh:borderFill id="(\d+)".*?</hh:borderFill>', header, re.DOTALL)

print(f"\n총 {len(border_fills)}개 borderFill 정의")

for bf_id in ['3', '19', '6', '7', '8']:  # 주요 ID들
    pattern = f'<hh:borderFill id="{bf_id}".*?</hh:borderFill>'
    match = re.search(pattern, header, re.DOTALL)
    
    if match:
        bf_xml = match.group(0)
        
        # 배경색 확인
        fill_color = re.search(r'<hh:fillBrush.*?color="([^"]*)"', bf_xml)
        
        print(f"\nborderFillIDRef=\"{bf_id}\":")
        if fill_color:
            print(f"  배경색: {fill_color.group(1)}")
        else:
            print(f"  배경색: 없음 (투명/흰색)")
        
        # 처음 200자
        print(f"  구조 (처음 200자):")
        print(f"  {bf_xml[:200]}...")

print("\n\n" + "="*80)
print("결론:")
print("="*80)
print("""
표 셀 borderFillIDRef 매핑:
- 헤더 행 (첫 번째 행): borderFillIDRef="19" (회색 배경?)
- 데이터 행 (나머지 행): borderFillIDRef="?" (흰색 배경)

→ 정확한 ID를 확인하여 적용 필요
""")

