"""
표 구조 정확히 추출
"""
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('hwp/analyze_original/Contents/section2.xml', 'r', encoding='utf-8') as f:
    content = f.read()

# hp:tbl 시작 위치 찾기
start_pos = content.find('<hp:tbl')
end_pos = None

if start_pos == -1:
    print("표를 찾을 수 없습니다")
    sys.exit(1)

# 매칭되는 </hp:tbl> 찾기
depth = 0
i = start_pos

while i < len(content):
    if content[i:i+8] == '<hp:tbl':
        depth += 1
    elif content[i:i+9] == '</hp:tbl>':
        depth -= 1
        if depth == 0:
            end_pos = i + 9
            break
    i += 1

if end_pos:
    # 표 XML 추출
    table_xml = content[start_pos:end_pos]
else:
    print("표 끝을 찾을 수 없습니다")
    sys.exit(1)
    
    print(f"표 추출 완료: {len(table_xml):,}자")
    
    # 파일로 저장
    with open('hwp/extracted_table.xml', 'w', encoding='utf-8') as f:
        f.write(table_xml)
    
    print(f"✓ 저장: hwp/extracted_table.xml")
    
    # 행별 borderFillIDRef 분석
    print("\n" + "="*80)
    print("행별 셀 borderFillIDRef 분석")
    print("="*80)
    
    import re
    rows = re.findall(r'<hp:tr>(.*?)</hp:tr>', table_xml, re.DOTALL)
    
    for row_idx, row in enumerate(rows, 1):
        print(f"\n행 {row_idx}:")
        
        # 셀의 borderFillIDRef 찾기
        cells_border = re.findall(r'<hp:tc[^>]*borderFillIDRef="(\d+)"', row)
        
        if cells_border:
            print(f"  borderFillIDRef: {set(cells_border)}")
        else:
            print(f"  borderFillIDRef: 없음")
        
        # header 속성
        cells_header = re.findall(r'<hp:tc[^>]*header="(\d+)"', row)
        if cells_header:
            print(f"  header 속성: {set(cells_header)}")
    
    # 첫 3000자 출력
    print("\n\n" + "="*80)
    print("표 XML (처음 3000자)")
    print("="*80)
    print(table_xml[:3000])

