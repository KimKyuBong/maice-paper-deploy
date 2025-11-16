"""
주요 borderFill의 테두리 패턴 명확히 표시
"""
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

tree = ET.parse('hwp/analyze_original/Contents/header.xml')
root = tree.getroot()
ns = {'hh': 'http://www.hancom.co.kr/hwpml/2011/head'}

# 분석할 ID들
ids_to_check = ['7', '8', '10', '11', '12', '13', '14', '15', '17', '19', '21', '22']

print("="*80)
print("표 테두리 패턴 완전 분석")
print("="*80)

for bf_id in ids_to_check:
    bf = root.find(f'.//hh:borderFill[@id="{bf_id}"]', ns)
    
    if bf is not None:
        left = bf.find('hh:leftBorder', ns)
        right = bf.find('hh:rightBorder', ns)
        top = bf.find('hh:topBorder', ns)
        bottom = bf.find('hh:bottomBorder', ns)
        
        def border_str(b):
            if b is None:
                return "없음"
            t = b.get('type', 'N/A')
            w = b.get('width', 'N/A')
            c = b.get('color', 'N/A')
            if t == 'NONE':
                return "NONE"
            return f"{t} {w} {c}"
        
        print(f"\nborderFillIDRef=\"{bf_id}\":")
        print(f"  왼쪽:  {border_str(left)}")
        print(f"  오른쪽: {border_str(right)}")
        print(f"  위:    {border_str(top)}")
        print(f"  아래:  {border_str(bottom)}")

print("\n\n" + "="*80)
print("권장 매핑 (간단한 표 기준)")
print("="*80)
print("""
헤더 행:
  - 맨왼쪽: 19 (왼쪽 NONE, 오른쪽 SOLID, 위/아래 굵게)
  - 중간:   12 (왼쪽/오른쪽 SOLID, 위/아래 굵게)  
  - 맨오른쪽: 17 (왼쪽 SOLID, 오른쪽 NONE, 위/아래 굵게)

데이터 행:
  - 맨왼쪽: 11 (왼쪽 NONE, 오른쪽 SOLID)
  - 중간:   13 (왼쪽/오른쪽 SOLID)
  - 맨오른쪽: 14 (왼쪽 SOLID, 오른쪽 NONE)

맨아래 행:
  - 맨왼쪽: 10
  - 중간:   10
  - 맨오른쪽: 15
""")

