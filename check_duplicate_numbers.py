"""
생성된 HWPX에서 중복 번호 확인
"""
import sys
import zipfile
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

hwpx = "hwp/report_with_images_20251112_043219.hwpx"

with zipfile.ZipFile(hwpx, 'r') as zf:
    xml = zf.read('Contents/section2.xml').decode('utf-8')
    tree = ET.fromstring(xml.encode('utf-8'))
    
    ns = {'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph'}
    
    # heading 스타일 찾기 (styleIDRef 5-9)
    headings = []
    for p in tree.findall('.//hp:p', ns):
        style_id = p.get('styleIDRef')
        
        if style_id in ['5', '6', '7', '8', '9']:
            # 텍스트 추출
            texts = []
            for t in p.findall('.//hp:t', ns):
                if t.text:
                    texts.append(t.text)
            
            if texts:
                full_text = ''.join(texts)
                headings.append({
                    'style': f'heading{int(style_id)-4}',
                    'text': full_text
                })

print("="*80)
print("제목 목록 (처음 30개)")
print("="*80)

for i, h in enumerate(headings[:30], 1):
    # 중복 패턴 확인
    import re
    if re.match(r'^\d+\.\s*\d+\.', h['text']):  # "1. 1." 패턴
        marker = " ⚠️ 중복!"
    elif re.match(r'^[가-힣]\.\s*[가-힣]\.', h['text']):  # "가. 가." 패턴
        marker = " ⚠️ 중복!"
    else:
        marker = ""
    
    print(f"{i}. [{h['style']}] {h['text'][:80]}{marker}")

