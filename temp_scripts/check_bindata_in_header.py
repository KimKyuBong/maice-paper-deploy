"""
header.xml의 binData 섹션 확인
"""
import sys
import zipfile
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("header.xml의 binData 확인")
print("="*80)

# 원본 파일
original_file = "hwp/report_backup_20251112_020239.hwpx"
with zipfile.ZipFile(original_file, 'r') as zf:
    header_xml = zf.read('Contents/header.xml').decode('utf-8')
    
    # binData 섹션 찾기
    if '<hh:binData>' in header_xml:
        print("\n원본 header.xml:")
        print("✓ <hh:binData> 섹션 존재")
        
        # binData 추출
        start = header_xml.find('<hh:binData>')
        end = header_xml.find('</hh:binData>') + len('</hh:binData>')
        bindata_section = header_xml[start:end]
        
        # 파싱
        bindata_elem = ET.fromstring(bindata_section)
        
        # 자식 요소 확인
        print(f"  등록된 이미지 수: {len(bindata_elem)}개")
        
        # 처음 3개 출력
        for i, child in enumerate(list(bindata_elem)[:3], 1):
            print(f"\n  이미지 {i}:")
            print(f"    태그: {child.tag}")
            for key, val in child.attrib.items():
                print(f"    {key}: {val}")
    else:
        print("✗ <hh:binData> 섹션 없음")

# 생성된 파일
print("\n" + "="*80)
generated_file = "hwp/report_updated_with_images.hwpx"
with zipfile.ZipFile(generated_file, 'r') as zf:
    header_xml = zf.read('Contents/header.xml').decode('utf-8')
    
    if '<hh:binData>' in header_xml:
        print("생성된 header.xml:")
        print("✓ <hh:binData> 섹션 존재")
        
        start = header_xml.find('<hh:binData>')
        end = header_xml.find('</hh:binData>') + len('</hh:binData>')
        bindata_section = header_xml[start:end]
        
        bindata_elem = ET.fromstring(bindata_section)
        print(f"  등록된 이미지 수: {len(bindata_elem)}개")
        
        # diagram으로 시작하는 것만 찾기
        diagram_items = [child for child in bindata_elem if child.get('id', '').startswith('diagram')]
        print(f"  diagram 이미지: {len(diagram_items)}개")
        
        if diagram_items:
            print("\n  등록된 diagram들:")
            for item in diagram_items:
                print(f"    - {item.get('id')}: {item.get('name')}")
        else:
            print("\n  ✗ diagram 이미지가 등록되지 않음!")
    else:
        print("생성된 header.xml:")
        print("✗ <hh:binData> 섹션 없음")

print("\n" + "="*80)
print("결론:")
print("="*80)
print("""
이미지가 표시되지 않는 이유:
1. header.xml의 <hh:binData> 섹션에 diagram 이미지가 등록되지 않았을 가능성
2. 이미지 정보(크기, 포맷 등)가 등록되어야 함

해결 방법:
- copy_images_to_bindata() 함수에서 header.xml도 업데이트해야 함
""")

