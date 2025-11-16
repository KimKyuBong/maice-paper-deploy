"""
원본 section2.xml에서 이미지 XML 전체 추출
"""
import sys
import zipfile

sys.stdout.reconfigure(encoding='utf-8')

original_file = "hwp/report_backup_20251112_020239.hwpx"

with zipfile.ZipFile(original_file, 'r') as zf:
    xml = zf.read('Contents/section2.xml').decode('utf-8')
    
    # 첫 번째 <hp:pic>부터 </hp:pic>까지 추출
    start = xml.find('<hp:pic ')
    if start != -1:
        # 매칭되는 </hp:pic> 찾기
        depth = 1
        pos = start + len('<hp:pic')
        
        # > 찾기
        while pos < len(xml) and xml[pos] != '>':
            pos += 1
        pos += 1  # > 다음으로
        
        # 매칭되는 닫는 태그 찾기
        while pos < len(xml) and depth > 0:
            if xml[pos:pos+8] == '<hp:pic ':
                depth += 1
            elif xml[pos:pos+9] == '</hp:pic>':
                depth -= 1
                if depth == 0:
                    pos += 9
                    break
            pos += 1
        
        pic_xml = xml[start:pos]
        
        print("="*80)
        print("원본 첫 번째 이미지 XML (완전한 형태)")
        print("="*80)
        print(pic_xml[:2000])
        print("\n...")
        print(pic_xml[-500:])
        
        # 파일에 저장
        with open('hwp/original_pic_template.xml', 'w', encoding='utf-8') as f:
            f.write(pic_xml)
        
        print(f"\n✓ 저장 완료: hwp/original_pic_template.xml ({len(pic_xml)} bytes)")

