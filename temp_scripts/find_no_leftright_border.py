"""
좌우 테두리가 없는 borderFill 찾기
"""
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("좌우 테두리 없는 borderFill 찾기")
print("="*80)

tree = ET.parse('hwp/analyze_original/Contents/header.xml')
root = tree.getroot()

ns = {'hh': 'http://www.hancom.co.kr/hwpml/2011/head'}

border_fills = root.findall('.//hh:borderFill', ns)

print(f"\n총 {len(border_fills)}개 borderFill 검사\n")

candidates = []

for bf in border_fills:
    bf_id = bf.get('id')
    
    # 각 테두리 확인
    left = bf.find('hh:leftBorder', ns)
    right = bf.find('hh:rightBorder', ns)
    top = bf.find('hh:topBorder', ns)
    bottom = bf.find('hh:bottomBorder', ns)
    
    left_type = left.get('type') if left is not None else 'N/A'
    right_type = right.get('type') if right is not None else 'N/A'
    top_type = top.get('type') if top is not None else 'N/A'
    bottom_type = bottom.get('type') if bottom is not None else 'N/A'
    
    # 좌우 없고, 위아래만 있는 것
    if (left_type == 'NONE' and right_type == 'NONE' and 
        top_type == 'SOLID' and bottom_type == 'SOLID'):
        
        top_color = top.get('color') if top is not None else 'N/A'
        bottom_color = bottom.get('color') if bottom is not None else 'N/A'
        
        candidates.append({
            'id': bf_id,
            'top_color': top_color,
            'bottom_color': bottom_color,
            'top_width': top.get('width') if top is not None else 'N/A',
            'bottom_width': bottom.get('width') if bottom is not None else 'N/A'
        })

print(f"좌우 테두리 없고 위아래만 있는 borderFill:")
print("-"*80)

for candidate in candidates:
    print(f"\nborderFillIDRef=\"{candidate['id']}\":")
    print(f"  위: {candidate['top_width']}, {candidate['top_color']}")
    print(f"  아래: {candidate['bottom_width']}, {candidate['bottom_color']}")

if not candidates:
    print("\n⚠️ 정확히 일치하는 것을 못 찾았습니다.")
    print("좌우 NONE이 아닌 다른 패턴 찾기...\n")
    
    # 좌우가 얇거나 다른 패턴
    for bf in border_fills[:20]:
        bf_id = bf.get('id')
        
        left = bf.find('hh:leftBorder', ns)
        right = bf.find('hh:rightBorder', ns)
        top = bf.find('hh:topBorder', ns)
        bottom = bf.find('hh:bottomBorder', ns)
        
        left_type = left.get('type') if left is not None else 'N/A'
        right_type = right.get('type') if right is not None else 'N/A'
        
        if left_type == 'NONE' or right_type == 'NONE':
            print(f"\nborderFillIDRef=\"{bf_id}\":")
            print(f"  left: {left_type}")
            print(f"  right: {right_type}")
            if top is not None:
                print(f"  top: {top.get('type')}, {top.get('width')}, {top.get('color')}")
            if bottom is not None:
                print(f"  bottom: {bottom.get('type')}, {bottom.get('width')}, {bottom.get('color')}")

print("\n\n" + "="*80)
print("권장 사항:")
print("="*80)

if candidates:
    print(f"""
일반 데이터 셀에 borderFillIDRef="{candidates[0]['id']}" 사용
→ 좌우 테두리 없음, 위아래 회색 테두리
""")
else:
    print("""
새로운 borderFill 정의를 추가하거나
기존 것 중 가장 가까운 것 사용
""")

