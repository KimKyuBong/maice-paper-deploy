"""
pyhwpx 기본 기능 테스트 스크립트
"""
import pyhwpx
import os
import sys

# 콘솔 인코딩 설정
sys.stdout.reconfigure(encoding='utf-8')

def test_create_simple_hwp():
    """간단한 HWP 문서 생성 테스트"""
    print("=== pyhwpx 기본 기능 테스트 ===\n")
    
    # HWP 문서 생성
    hwp = pyhwpx.Hwp()
    
    # 제목 텍스트 추가
    hwp.insert_text("pyhwpx 테스트 문서")
    hwp.set_font(Height=20, Bold=True)
    hwp.insert_enter()
    hwp.insert_enter()
    
    # 본문 내용
    hwp.set_font(Height=10, Bold=False)
    hwp.insert_text("이 문서는 pyhwpx를 사용하여 자동으로 생성되었습니다.")
    hwp.insert_enter()
    hwp.insert_enter()
    
    # 표 추가
    hwp.insert_text("아래는 샘플 표입니다:")
    hwp.insert_enter()
    hwp.insert_table(rows=3, cols=3)
    
    # 저장 경로 생성
    save_path = os.path.join("hwp", "test_document.hwp")
    os.makedirs("hwp", exist_ok=True)
    
    # 문서 저장
    hwp.save(save_path)
    hwp.quit()
    
    print(f"문서가 생성되었습니다: {save_path}")
    return save_path

def test_read_hwp(file_path):
    """HWP 문서 읽기 테스트"""
    if not os.path.exists(file_path):
        print(f"파일이 존재하지 않습니다: {file_path}")
        return
    
    print("\n=== HWP 문서 읽기 테스트 ===\n")
    
    hwp = pyhwpx.Hwp()
    hwp.open(file_path)
    
    # 텍스트 추출
    text = hwp.get_text()
    print("문서 내용:")
    print("-" * 50)
    print(text)
    print("-" * 50)
    
    hwp.quit()
    print("\n문서를 성공적으로 읽었습니다.")

def test_advanced_features():
    """고급 기능 테스트"""
    print("\n=== pyhwpx 고급 기능 테스트 ===\n")
    
    hwp = pyhwpx.Hwp()
    
    # 제목
    hwp.insert_text("고급 기능 테스트 문서")
    hwp.set_font(Height=16, Bold=True, FaceName="맑은 고딕")
    hwp.insert_enter()
    hwp.insert_enter()
    
    # 다양한 서식 적용
    hwp.set_font(Height=11, Bold=False)
    hwp.insert_text("1. 볼드체: ")
    hwp.set_font(Bold=True)
    hwp.insert_text("중요한 내용")
    hwp.set_font(Bold=False)
    hwp.insert_enter()
    
    hwp.insert_text("2. 이탤릭: ")
    hwp.set_font(Italic=True)
    hwp.insert_text("강조된 내용")
    hwp.set_font(Italic=False)
    hwp.insert_enter()
    
    hwp.insert_text("3. 밑줄: ")
    hwp.set_font(UnderlineType=1)
    hwp.insert_text("밑줄 친 내용")
    hwp.set_font(UnderlineType=0)
    hwp.insert_enter()
    hwp.insert_enter()
    
    # 데이터가 포함된 표 생성
    hwp.insert_text("성적표 예시:")
    hwp.insert_enter()
    
    table_data = [
        ["이름", "수학", "영어", "과학"],
        ["학생1", "90", "85", "88"],
        ["학생2", "85", "92", "90"],
        ["학생3", "88", "87", "95"]
    ]
    
    # 표 삽입
    hwp.insert_table(rows=4, cols=4)
    
    save_path = os.path.join("hwp", "advanced_test.hwp")
    hwp.save(save_path)
    hwp.quit()
    
    print(f"고급 기능 문서가 생성되었습니다: {save_path}")

if __name__ == "__main__":
    try:
        # 기본 문서 생성 테스트
        doc_path = test_create_simple_hwp()
        
        # 문서 읽기 테스트
        test_read_hwp(doc_path)
        
        # 고급 기능 테스트
        test_advanced_features()
        
        print("\n모든 테스트가 완료되었습니다!")
        
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()

