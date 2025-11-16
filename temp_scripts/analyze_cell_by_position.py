"""
표 셀의 위치별 borderFillIDRef 분석
"""
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("셀 위치별 borderFillIDRef 분석")
print("="*80)

tree = ET.parse('hwp/analyze_original/Contents/section2.xml')
root = tree.getroot()

ns = {
    'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph',
}

# 첫 번째 표
tables = root.findall('.//hp:tbl', ns)

if tables:
    first_table = tables[0]
    
    row_cnt = int(first_table.get('rowCnt', 0))
    col_cnt = int(first_table.get('colCnt', 0))
    
    print(f"\n첫 번째 표: {row_cnt}행 x {col_cnt}열\n")
    
    rows = first_table.findall('hp:tr', ns)
    
    print("="*80)
    print("위치별 borderFillIDRef 매핑")
    print("="*80)
    
    for row_idx, row in enumerate(rows):
        cells = row.findall('hp:tc', ns)
        
        print(f"\n행 {row_idx + 1}:")
        
        for cell_idx, cell in enumerate(cells):
            border_fill = cell.get('borderFillIDRef')
            
            # 셀 주소
            cell_addr = cell.find('hp:cellAddr', ns)
            col_addr = cell_addr.get('colAddr') if cell_addr is not None else '?'
            row_addr = cell_addr.get('rowAddr') if cell_addr is not None else '?'
            
            # 텍스트
            texts = cell.findall('.//hp:t', ns)
            text = ''.join([t.text for t in texts if t.text])[:30]
            
            # 위치 분류
            position = []
            if cell_idx == 0:
                position.append("맨왼쪽")
            if cell_idx == len(cells) - 1:
                position.append("맨오른쪽")
            if row_idx == 0:
                position.append("맨위(헤더)")
            if row_idx == len(rows) - 1:
                position.append("맨아래")
            if not position:
                position.append("중간")
            
            pos_str = ', '.join(position)
            
            print(f"  셀[{row_addr},{col_addr}] ({pos_str:20s}): borderFill={border_fill:2s} | {text}")

print("\n\n" + "="*80)
print("패턴 요약")
print("="*80)

# 위치별 borderFill 매핑 분석
print("""
예상 패턴:
- 헤더 행 + 맨왼쪽: borderFillIDRef="?"
- 헤더 행 + 중간: borderFillIDRef="?"
- 헤더 행 + 맨오른쪽: borderFillIDRef="?"
- 데이터 행 + 맨왼쪽: borderFillIDRef="?"
- 데이터 행 + 중간: borderFillIDRef="?"
- 데이터 행 + 맨오른쪽: borderFillIDRef="?"
- 맨아래 행: borderFillIDRef="?"

→ 위 분석 결과를 바탕으로 정확한 ID 매핑
""")

