"""
이미지 구조 완전 추출
"""
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('hwp/analyze_original/Contents/section2.xml', 'r', encoding='utf-8') as f:
    content = f.read()

print("="*80)
print("이미지 구조 완전 추출")
print("="*80)

# imgRect 전후 컨텍스트 추출
img_pos = content.find('<hp:imgRect')

if img_pos != -1:
    # 이미지를 포함하는 ctrl 태그 찾기
    # 뒤로 가서 <hp:ctrl> 찾기
    ctrl_start = content.rfind('<hp:ctrl>', 0, img_pos)
    
    if ctrl_start != -1:
        # 매칭되는 </hp:ctrl> 찾기
        ctrl_end = content.find('</hp:ctrl>', img_pos)
        
        if ctrl_end != -1:
            img_ctrl = content[ctrl_start:ctrl_end + 10]
            
            print(f"\n이미지 컨트롤 추출 완료: {len(img_ctrl):,}자")
            
            # 파일로 저장
            with open('hwp/extracted_image_ctrl.xml', 'w', encoding='utf-8') as f:
                f.write(img_ctrl)
            
            print(f"✓ 저장: hwp/extracted_image_ctrl.xml")
            
            # 구조 표시 (처음 1500자)
            print(f"\nXML 구조 (처음 1500자):")
            print("="*80)
            print(img_ctrl[:1500])
            print("...")
            
            # 주요 속성 추출
            print("\n\n주요 속성:")
            print("-"*80)
            
            # 그림 크기
            width = re.search(r'width="(\d+)"', img_ctrl)
            height = re.search(r'height="(\d+)"', img_ctrl)
            
            if width and height:
                print(f"크기: width={width.group(1)}, height={height.group(1)}")
            
            # zOrder
            zorder = re.search(r'zOrder="(\d+)"', img_ctrl)
            if zorder:
                print(f"zOrder: {zorder.group(1)}")

print("\n" + "="*80)
print("완료")
print("="*80)

