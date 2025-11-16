"""
빠른 이미지 확인
"""
import sys
import zipfile
import re

sys.stdout.reconfigure(encoding='utf-8')

hwpx = "hwp/report_with_images_20251112_033511.hwpx"

with zipfile.ZipFile(hwpx, 'r') as zf:
    xml = zf.read('Contents/section2.xml').decode('utf-8')
    
    # 1. <hp:pic> 태그 개수
    pic_count = xml.count('<hp:pic ')
    print(f"<hp:pic> 태그: {pic_count}개")
    
    # 2. diagram 참조 개수
    diagram_refs = re.findall(r'binaryItemIDRef="(diagram\d+)"', xml)
    print(f"\ndiagram 참조: {len(diagram_refs)}개")
    for ref in diagram_refs:
        print(f"  - {ref}")
    
    # 3. [MERMAID: 또는 [IMAGE_PLACEHOLDER: 텍스트가 남아있는지
    if '[MERMAID:' in xml or '[IMAGE_PLACEHOLDER:' in xml:
        print("\n⚠️ 경고: 플레이스홀더가 치환되지 않음!")
        placeholders = re.findall(r'\[(MERMAID|IMAGE_PLACEHOLDER):[^\]]+\]', xml)
        print(f"  남은 플레이스홀더: {len(placeholders)}개")
        for ph in placeholders[:3]:
            print(f"    {ph}")
    else:
        print("\n✓ 플레이스홀더 모두 치환됨")
    
    # 4. 이미지가 있는 위치 주변 텍스트 확인
    print("\n이미지 위치 확인:")
    for i, match in enumerate(re.finditer(r'<hp:pic [^>]*binaryItemIDRef="(diagram\d+)"', xml), 1):
        ref = match.group(1)
        pos = match.start()
        
        # 이전 500자 추출
        before = xml[max(0, pos-500):pos]
        
        # 텍스트 찾기
        texts = re.findall(r'<hp:t>([^<]+)</hp:t>', before)
        if texts:
            context = texts[-1][:80] if texts else ""
            print(f"  {i}. {ref}: ...{context}")
        else:
            print(f"  {i}. {ref}: (텍스트 없음)")

