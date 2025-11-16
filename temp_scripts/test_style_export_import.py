"""
HWP 스타일 Export/Import 테스트
"""
import pyhwpx
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("스타일 Export/Import 테스트")
print("="*80)

# 1. 기존 문서에서 스타일 추출
print("\n1단계: 스타일 추출")
print("-"*80)

original_hwp = os.path.abspath("hwp/report.hwpx")
style_file = os.path.abspath("hwp/exported_styles.sty")

print(f"원본 파일: {original_hwp}")
print(f"스타일 파일: {style_file}")

hwp1 = pyhwpx.Hwp()
print("✓ HWP 객체 생성")

hwp1.open(original_hwp)
print("✓ 원본 문서 열기 완료")

try:
    result = hwp1.export_style(style_file)
    print(f"\nexport_style 결과: {result}")
    
    if os.path.exists(style_file):
        size = os.path.getsize(style_file)
        print(f"✓ 스타일 파일 생성 완료: {size:,} bytes")
    else:
        print("✗ 스타일 파일이 생성되지 않았습니다")
        
except Exception as e:
    print(f"✗ export_style 오류: {e}")
    import traceback
    traceback.print_exc()

hwp1.quit()
print("\n원본 문서 닫기 완료")

# 2. 새 문서에 스타일 적용 테스트
if os.path.exists(style_file):
    print("\n2단계: 새 문서에 스타일 적용")
    print("-"*80)
    
    hwp2 = pyhwpx.Hwp()
    print("✓ 새 문서 생성")
    
    try:
        result = hwp2.import_style(style_file)
        print(f"\nimport_style 결과: {result}")
        
        # 가져온 스타일 확인
        styles = hwp2.get_style_dict()
        print(f"✓ 가져온 스타일 수: {len(styles)}개")
        
        # 스타일 적용 테스트
        print("\n3단계: 스타일 적용 테스트")
        print("-"*80)
        
        # 본문 스타일
        hwp2.insert_text("이것은 본문 스타일 테스트입니다.")
        hwp2.set_style("본문")
        hwp2.BreakPara()
        print("✓ '본문' 스타일 적용")
        
        # 제목1 스타일
        hwp2.insert_text("Ⅰ. 제목 스타일 테스트")
        hwp2.set_style("Ⅰ. 제목")
        hwp2.BreakPara()
        print("✓ 'Ⅰ. 제목' 스타일 적용")
        
        # 제목2 스타일
        hwp2.insert_text("1. 중제목 스타일 테스트")
        hwp2.set_style("1. 제목")
        hwp2.BreakPara()
        print("✓ '1. 제목' 스타일 적용")
        
        # 제목3 스타일
        hwp2.insert_text("가. 소제목 스타일 테스트")
        hwp2.set_style("가. 제목")
        hwp2.BreakPara()
        print("✓ '가. 제목' 스타일 적용")
        
        # 저장
        test_output = os.path.abspath("hwp/style_test.hwpx")
        save_result = hwp2.save(test_output)
        print(f"\n저장 결과: {save_result}")
        
        if save_result and os.path.exists(test_output):
            print(f"✓ 테스트 문서 생성: {test_output}")
        
    except Exception as e:
        print(f"✗ 오류: {e}")
        import traceback
        traceback.print_exc()
    
    hwp2.quit()

print("\n" + "="*80)
print("테스트 완료!")
print("="*80)

if os.path.exists(style_file):
    print(f"\n✓ 스타일 파일: {style_file}")
if os.path.exists("hwp/style_test.hwpx"):
    print(f"✓ 테스트 문서: hwp/style_test.hwpx")
    print("\n→ 파일을 열어서 스타일이 제대로 적용되었는지 확인해주세요!")

