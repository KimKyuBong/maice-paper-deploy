"""
원본에서 이미지가 포함된 문단 전체 구조 추출
"""
import sys
import zipfile

sys.stdout.reconfigure(encoding='utf-8')

original = "hwp/report_backup_20251112_020239.hwpx"

with zipfile.ZipFile(original, 'r') as zf:
    xml = zf.read('Contents/section2.xml').decode('utf-8')
    
    # 첫 번째 <hp:pic>를 포함한 <hp:p> 전체 추출
    pic_start = xml.find('<hp:pic ')
    
    if pic_start != -1:
        # <hp:pic> 이전의 <hp:p> 찾기
        p_start = xml.rfind('<hp:p ', 0, pic_start)
        
        if p_start != -1:
            # </hp:p> 찾기
            p_end = xml.find('</hp:p>', pic_start) + len('</hp:p>')
            
            para_xml = xml[p_start:p_end]
            
            print("="*80)
            print("원본: 이미지를 포함한 문단 전체")
            print("="*80)
            print(para_xml[:1500])
            print("\n...")
            print(para_xml[-500:])
            
            # 파일 저장
            with open('hwp/original_image_paragraph.xml', 'w', encoding='utf-8') as f:
                f.write(para_xml)
            
            print(f"\n✓ 저장: hwp/original_image_paragraph.xml ({len(para_xml)} bytes)")
            
            # 구조 분석
            print("\n" + "="*80)
            print("구조 분석:")
            print("="*80)
            
            if '<hp:ctrl>' in para_xml:
                print("✓ <hp:ctrl> 태그 사용")
            else:
                print("✗ <hp:ctrl> 태그 없음")
            
            if '<hp:run' in para_xml:
                print("✓ <hp:run> 태그 사용")
                # run 개수
                run_count = para_xml.count('<hp:run ')
                print(f"  run 개수: {run_count}개")
            
            if 'paraPrIDRef=' in para_xml:
                import re
                para_pr = re.search(r'paraPrIDRef="(\d+)"', para_xml)
                if para_pr:
                    print(f"✓ paraPrIDRef: {para_pr.group(1)}")
            
            if 'styleIDRef=' in para_xml:
                import re
                style = re.search(r'styleIDRef="(\d+)"', para_xml)
                if style:
                    print(f"✓ styleIDRef: {style.group(1)}")

