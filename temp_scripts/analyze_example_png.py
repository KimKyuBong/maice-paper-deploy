"""
example.hwpx의 PNG 이미지 구조 분석
"""
import sys
import zipfile
import os
import shutil
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

example_file = "hwp/example.hwpx"

print("="*80)
print("example.hwpx PNG 이미지 분석")
print("="*80)

# 압축 해제
extract_dir = "hwp/example_extracted"
if os.path.exists(extract_dir):
    shutil.rmtree(extract_dir)

with zipfile.ZipFile(example_file, 'r') as zf:
    zf.extractall(extract_dir)

print("✓ 압축 해제 완료")

# 1. BinData 확인
bindata_dir = os.path.join(extract_dir, "BinData")
if os.path.exists(bindata_dir):
    files = os.listdir(bindata_dir)
    print(f"\n1. BinData 파일 ({len(files)}개):")
    for f in sorted(files)[:20]:
        path = os.path.join(bindata_dir, f)
        size = os.path.getsize(path)
        ext = f.split('.')[-1].upper()
        print(f"  {f} ({size:,} bytes) - {ext}")

# 2. section2.xml에서 이미지 찾기
section2_path = os.path.join(extract_dir, "Contents", "section2.xml")
with open(section2_path, 'r', encoding='utf-8') as f:
    xml_content = f.read()

tree = ET.fromstring(xml_content.encode('utf-8'))
ns = {
    'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph',
    'hc': 'http://www.hancom.co.kr/hwpml/2011/core'
}

pics = tree.findall('.//hp:pic', ns)
print(f"\n2. section2.xml의 이미지: {len(pics)}개")

for i, pic in enumerate(pics[:5], 1):
    img_elem = pic.find('.//hc:img', ns)
    if img_elem is not None:
        ref = img_elem.get('binaryItemIDRef')
        
        # orgSz, curSz 확인
        org_sz = pic.find('.//hp:orgSz', ns)
        cur_sz = pic.find('.//hp:curSz', ns)
        
        org_w = org_sz.get('width') if org_sz is not None else '?'
        org_h = org_sz.get('height') if org_sz is not None else '?'
        cur_w = cur_sz.get('width') if cur_sz is not None else '?'
        cur_h = cur_sz.get('height') if cur_sz is not None else '?'
        
        # scaMatrix 확인
        sca_matrix = pic.find('.//hc:scaMatrix', ns)
        scale_x = sca_matrix.get('e1') if sca_matrix is not None else '?'
        scale_y = sca_matrix.get('e5') if sca_matrix is not None else '?'
        
        print(f"\n  이미지 {i}: {ref}")
        print(f"    orgSz: {org_w} x {org_h}")
        print(f"    curSz: {cur_w} x {cur_h}")
        print(f"    scale: {scale_x}, {scale_y}")

# 3. 첫 이미지 전체 XML 저장
if pics:
    pic_xml = ET.tostring(pics[0], encoding='unicode')
    
    with open('hwp/example_pic_template.xml', 'w', encoding='utf-8') as f:
        f.write(pic_xml)
    
    print(f"\n✓ 첫 이미지 XML 저장: hwp/example_pic_template.xml")
    print(f"  처음 500자:")
    print(pic_xml[:500])

# 4. 첫 이미지 문단 전체 추출
pic_start = xml_content.find('<hp:pic ')
p_start = xml_content.rfind('<hp:p ', 0, pic_start)
p_end = xml_content.find('</hp:p>', pic_start) + len('</hp:p>')

para_xml = xml_content[p_start:p_end]

with open('hwp/example_image_paragraph.xml', 'w', encoding='utf-8') as f:
    f.write(para_xml)

print(f"\n✓ 첫 이미지 문단 저장: hwp/example_image_paragraph.xml ({len(para_xml)} bytes)")

print("\n" + "="*80)
print("완료!")
print("="*80)

