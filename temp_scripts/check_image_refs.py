"""
이미지 참조 확인
"""
import sys
import zipfile
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

hwpx_file = "hwp/report_updated_with_images.hwpx"

print("="*80)
print("이미지 참조 확인")
print("="*80)

with zipfile.ZipFile(hwpx_file, 'r') as zf:
    # 1. BinData 폴더의 실제 파일명
    bindata_files = [f for f in zf.namelist() if f.startswith('BinData/')]
    print("\n1. BinData 폴더의 파일들:")
    for f in sorted(bindata_files):
        # 파일명만 추출
        filename = f.split('/')[-1]
        # 확장자 제거한 이름
        base_name = filename.rsplit('.', 1)[0]
        print(f"  {filename} → ID: {base_name}")
    
    # 2. section2.xml에서 이미지 참조 확인
    xml_content = zf.read('Contents/section2.xml').decode('utf-8')
    tree = ET.fromstring(xml_content.encode('utf-8'))
    
    ns = {
        'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph',
        'hc': 'http://www.hancom.co.kr/hwpml/2011/core'
    }
    
    print("\n2. section2.xml의 이미지 참조:")
    pics = tree.findall('.//hp:pic', ns)
    print(f"  총 {len(pics)}개 이미지")
    
    for i, pic in enumerate(pics, 1):
        # binaryItemIDRef 찾기
        img_elem = pic.find('.//hc:img', ns)
        if img_elem is not None:
            ref = img_elem.get('binaryItemIDRef')
            print(f"  이미지 {i}: binaryItemIDRef='{ref}'")
            
            # 해당 파일이 BinData에 있는지 확인
            expected_files = [
                f"BinData/{ref}",
                f"BinData/{ref}.BMP",
                f"BinData/{ref}.PNG",
                f"BinData/{ref}.png"
            ]
            
            found = False
            for ef in expected_files:
                if ef in bindata_files:
                    print(f"    ✓ 파일 존재: {ef}")
                    found = True
                    break
            
            if not found:
                print(f"    ✗ 파일 없음! 찾는 이름: {ref}")
        else:
            print(f"  이미지 {i}: <hc:img> 요소 없음!")
    
    # 3. 원본과 비교
    print("\n3. 원본 파일과 비교:")
    original_file = "hwp/report_backup_20251112_020239.hwpx"
    
    with zipfile.ZipFile(original_file, 'r') as zf_orig:
        orig_xml = zf_orig.read('Contents/section2.xml').decode('utf-8')
        tree_orig = ET.fromstring(orig_xml.encode('utf-8'))
        
        pics_orig = tree_orig.findall('.//hp:pic', ns)
        print(f"  원본 이미지 수: {len(pics_orig)}개")
        
        if pics_orig:
            first_pic = pics_orig[0]
            img_elem = first_pic.find('.//hc:img', ns)
            if img_elem is not None:
                ref = img_elem.get('binaryItemIDRef')
                print(f"  원본 첫 이미지 참조: '{ref}'")
                
                # BinData 확인
                bindata_orig = [f for f in zf_orig.namelist() if f.startswith('BinData/')]
                print(f"  원본 BinData 파일 수: {len(bindata_orig)}개")
                print(f"  첫 번째 파일: {sorted(bindata_orig)[0] if bindata_orig else 'None'}")

