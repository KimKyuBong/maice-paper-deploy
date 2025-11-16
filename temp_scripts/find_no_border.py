"""
좌우 모두 NONE인 borderFill 찾기
"""
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

tree = ET.parse('hwp/analyze_original/Contents/header.xml')
root = tree.getroot()
ns = {'hh': 'http://www.hancom.co.kr/hwpml/2011/head'}

bfs = root.findall('.//hh:borderFill', ns)

print("="*80)
print("좌우 모두 NONE인 borderFill")
print("="*80)

found = []

for bf in bfs:
    bf_id = bf.get('id')
    left = bf.find('hh:leftBorder', ns)
    right = bf.find('hh:rightBorder', ns)
    top = bf.find('hh:topBorder', ns)
    bottom = bf.find('hh:bottomBorder', ns)
    
    left_type = left.get('type') if left is not None else None
    right_type = right.get('type') if right is not None else None
    top_type = top.get('type') if top is not None else None
    bottom_type = bottom.get('type') if bottom is not None else None
    
    if left_type == 'NONE' and right_type == 'NONE':
        top_width = top.get('width') if top is not None else 'N/A'
        bottom_width = bottom.get('width') if bottom is not None else 'N/A'
        top_color = top.get('color') if top is not None else 'N/A'
        
        found.append({
            'id': bf_id,
            'top': f"{top_type} {top_width} {top_color}",
            'bottom': f"{bottom_type} {bottom_width}"
        })
        
        print(f"\nborderFillIDRef=\"{bf_id}\":")
        print(f"  왼쪽: NONE")
        print(f"  오른쪽: NONE")
        print(f"  위: {top_type} {top_width} {top_color}")
        print(f"  아래: {bottom_type} {bottom_width}")

if not found:
    print("\n⚠️ 좌우 모두 NONE인 borderFill이 없습니다")
    print("새로 만들어야 합니다")
else:
    print("\n\n" + "="*80)
    print("권장 사용:")
    print("="*80)
    
    # 위아래가 SOLID인 것 찾기
    solid_ones = [f for f in found if 'SOLID' in f['top']]
    
    if solid_ones:
        print(f"\n중간 셀 (좌우 NONE, 위아래 SOLID):")
        for item in solid_ones:
            print(f"  → borderFillIDRef=\"{item['id']}\"")

