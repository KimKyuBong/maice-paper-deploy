"""
borderFill 정의 상세 분석 (테두리 스타일)
"""
import re
import sys
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("borderFill 상세 분석 (테두리 및 배경)")
print("="*80)

# header.xml 파싱
tree = ET.parse('hwp/analyze_original/Contents/header.xml')
root = tree.getroot()

ns = {'hh': 'http://www.hancom.co.kr/hwpml/2011/head'}

# borderFill 찾기
border_fills = root.findall('.//hh:borderFill', ns)
print(f"\n총 {len(border_fills)}개 borderFill 정의\n")

# 표에서 사용되는 주요 ID들 (3, 7, 19)
important_ids = ['3', '7', '19', '12', '13']

for bf_id in important_ids:
    bf = root.find(f'.//hh:borderFill[@id="{bf_id}"]', ns)
    
    if bf:
        print(f"\n{'='*80}")
        print(f"borderFillIDRef=\"{bf_id}\"")
        print(f"{'='*80}")
        
        # 테두리 정보
        for side in ['leftBorder', 'rightBorder', 'topBorder', 'bottomBorder']:
            border = bf.find(f'hh:{side}', ns)
            if border is not None:
                border_type = border.get('type')
                width = border.get('width')
                color = border.get('color')
                print(f"  {side:15s}: type={border_type}, width={width}, color={color}")
        
        # 배경 정보
        fill_brush = bf.find('.//hh:fillBrush', ns)
        if fill_brush is not None:
            fill_type = fill_brush.get('type')
            fill_color = fill_brush.get('color')
            print(f"  배경: type={fill_type}, color={fill_color}")
        else:
            print(f"  배경: 없음 (투명)")
        
        # 전체 XML (처음 400자)
        bf_str = ET.tostring(bf, encoding='unicode')
        print(f"\n  XML (처음 400자):")
        print(f"  {bf_str[:400]}")

# 표 전체 borderFillIDRef 확인
print("\n\n" + "="*80)
print("표 태그의 borderFillIDRef")
print("="*80)

tree2 = ET.parse('hwp/analyze_original/Contents/section2.xml')
root2 = tree2.getroot()

tables = root2.findall('.//hp:tbl', {'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph'})

if tables:
    first_table = tables[0]
    table_border = first_table.get('borderFillIDRef')
    print(f"\n첫 번째 <hp:tbl> 태그의 borderFillIDRef=\"{table_border}\"")
    print(f"→ 이것이 표 전체의 기본 테두리 스타일")

print("\n\n" + "="*80)
print("결론:")
print("="*80)
print("""
표 테두리 설정:
1. <hp:tbl borderFillIDRef="3"> ← 표 전체 기본 테두리
2. 헤더 셀: borderFillIDRef="19" ← 회색 배경 + 특정 테두리
3. 데이터 셀: borderFillIDRef="7" ← 흰색 배경 + 특정 테두리

각 borderFillIDRef는 테두리 선 종류, 두께, 색상을 포함
""")

