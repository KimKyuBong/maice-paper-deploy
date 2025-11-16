"""
기존 HWP 문서의 스타일 구조 분석
"""
import pyhwpx
import os
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

hwp_path = os.path.abspath("hwp/report.hwpx")

print("="*80)
print("HWP 문서 스타일 분석")
print("="*80)

hwp = pyhwpx.Hwp()
hwp.open(hwp_path)

print("\n📋 사용된 스타일 목록:")
print("-"*80)

try:
    # 스타일 딕셔너리 가져오기
    style_dict = hwp.get_used_style_dict()
    
    print(f"스타일 타입: {type(style_dict)}")
    
    if style_dict:
        print(f"총 {len(style_dict)}개의 스타일 사용 중:\n")
        if isinstance(style_dict, list):
            for style_name in style_dict:
                print(f"  - {style_name}")
        elif isinstance(style_dict, dict):
            for style_name, style_info in style_dict.items():
                print(f"  - {style_name}")
                if isinstance(style_info, dict):
                    for key, value in style_info.items():
                        print(f"      {key}: {value}")
    
    # 전체 스타일 목록
    print("\n\n📚 전체 스타일 딕셔너리:")
    print("-"*80)
    all_styles = hwp.get_style_dict()
    
    print(f"전체 스타일 타입: {type(all_styles)}")
    
    if all_styles:
        print(f"총 {len(all_styles)}개의 스타일 정의됨:\n")
        if isinstance(all_styles, dict):
            for i, (style_name, info) in enumerate(list(all_styles.items())[:20]):
                print(f"  {i+1}. {style_name}")
                if i >= 19:
                    print(f"  ... (총 {len(all_styles)}개 중 20개만 표시)")
                    break
        elif isinstance(all_styles, list):
            for i, style_name in enumerate(all_styles[:20]):
                print(f"  {i+1}. {style_name}")
                if i >= 19:
                    print(f"  ... (총 {len(all_styles)}개 중 20개만 표시)")
                    break
    
    # 현재 위치의 스타일 확인
    print("\n\n🔍 문서 시작 부분의 스타일 분석:")
    print("-"*80)
    
    hwp.Run("MoveDocBegin")
    
    # 서론 찾기
    if hwp.find("Ⅰ. 서 론"):
        current_style = hwp.get_style()
        print(f"\n'Ⅰ. 서 론' 위치의 스타일: {current_style}")
        
        # CharShape와 ParaShape 정보
        char_shape = hwp.get_charshape_as_dict()
        para_shape = hwp.get_parashape_as_dict()
        
        print("\n문자 서식 (CharShape):")
        if char_shape:
            for key, value in list(char_shape.items())[:10]:
                print(f"  {key}: {value}")
        
        print("\n문단 서식 (ParaShape):")
        if para_shape:
            for key, value in list(para_shape.items())[:10]:
                print(f"  {key}: {value}")
    
    # 특정 스타일로 이동 테스트
    print("\n\n🎯 스타일 기반 내비게이션 테스트:")
    print("-"*80)
    
    # 제목 스타일들 찾기
    hwp.Run("MoveDocBegin")
    for style_name in ["제목1", "제목 1", "Heading1", "Heading 1", "본문"]:
        result = hwp.goto_style(style_name)
        if result:
            text = hwp.get_selected_text()
            print(f"  ✓ '{style_name}' 스타일 찾음: {text[:50] if text else '(텍스트 없음)'}")
            break
    
except Exception as e:
    print(f"\n오류: {e}")
    import traceback
    traceback.print_exc()

# 스타일 정보를 JSON으로 저장
try:
    output = {
        "used_styles": style_dict if style_dict else {},
        "all_styles_count": len(all_styles) if all_styles else 0
    }
    
    with open("hwp/hwp_styles_info.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n\n💾 스타일 정보를 hwp/hwp_styles_info.json에 저장했습니다.")
except:
    pass

hwp.quit()

print("\n" + "="*80)
print("분석 완료!")
print("="*80)

