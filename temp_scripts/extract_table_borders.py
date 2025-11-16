"""
XML 파서로 표의 borderFillIDRef 정확히 추출
"""
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("표 borderFillIDRef 정확 추출")
print("="*80)

tree = ET.parse('hwp/analyze_original/Contents/section2.xml')
root = tree.getroot()

ns = {
    'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph',
    'hs': 'http://www.hancom.co.kr/hwpml/2011/section'
}

# 모든 표 찾기
tables = root.findall('.//hp:tbl', ns)
print(f"\n총 {len(tables)}개 표 발견\n")

if tables:
    # 첫 번째 표 분석
    first_table = tables[0]
    
    print("첫 번째 표 속성:")
    print(f"  id: {first_table.get('id')}")
    print(f"  rowCnt: {first_table.get('rowCnt')}")
    print(f"  colCnt: {first_table.get('colCnt')}")
    print(f"  borderFillIDRef: {first_table.get('borderFillIDRef')}")
    
    # 행들
    rows = first_table.findall('hp:tr', ns)
    print(f"\n행 개수: {len(rows)}")
    
    print("\n" + "="*80)
    print("행별 셀 borderFillIDRef 분석")
    print("="*80)
    
    for row_idx, row in enumerate(rows, 1):
        cells = row.findall('hp:tc', ns)
        
        print(f"\n행 {row_idx}: {len(cells)}개 셀")
        
        for cell_idx, cell in enumerate(cells[:3], 1):  # 처음 3개 셀만
            border_fill = cell.get('borderFillIDRef')
            header = cell.get('header')
            
            # 텍스트 추출
            texts = cell.findall('.//hp:t', ns)
            text = ''.join([t.text for t in texts if t.text])[:40]
            
            print(f"  셀 {cell_idx}:")
            print(f"    borderFillIDRef: {border_fill}")
            print(f"    header: {header}")
            print(f"    텍스트: {text}")

print("\n\n" + "="*80)
print("결론:")
print("="*80)
print("""
borderFillIDRef 정확한 값 확인 후:
- 헤더 행 셀: borderFillIDRef="?"
- 데이터 행 셀: borderFillIDRef="?"

→ 위 결과를 코드에 적용
""")

