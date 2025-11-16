"""
C1에 맞는 borderFill 찾기
- 좌 NONE
- 우 SOLID
- 아래 굵게 (0.7mm)
"""
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

tree = ET.parse('hwp/analyze_original/Contents/header.xml')
root = tree.getroot()
ns = {'hh': 'http://www.hancom.co.kr/hwpml/2011/head'}

bfs = root.findall('.//hh:borderFill', ns)

print("="*80)
print("C1용 borderFill 찾기: 좌 NONE, 우 SOLID, 아래 0.7mm")
print("="*80)

for bf in bfs:
    bf_id = bf.get('id')
    
    left = bf.find('hh:leftBorder', ns)
    right = bf.find('hh:rightBorder', ns)
    bottom = bf.find('hh:bottomBorder', ns)
    
    if (left is not None and right is not None and bottom is not None and
        left.get('type') == 'NONE' and 
        right.get('type') == 'SOLID' and
        bottom.get('width') == '0.7 mm'):
        
        top = bf.find('hh:topBorder', ns)
        
        print(f"\n✓ borderFillIDRef=\"{bf_id}\" 발견!")
        print(f"  좌: {left.get('type')}")
        print(f"  우: {right.get('type')} {right.get('width')}")
        print(f"  위: {top.get('type') if top else 'N/A'} {top.get('width') if top else ''}")
        print(f"  아래: {bottom.get('type')} {bottom.get('width')}")

print("\n" + "="*80)
print("결론:")
print("="*80)
print("기존 ID 중에 C1용이 있으면 그것 사용")
print("없으면 ID 52 (새로 만든 것) 사용")

