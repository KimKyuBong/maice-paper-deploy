"""
pyhwpx 간단한 테스트 스크립트 (공식 문서 기반)
참고: https://martiniifun.github.io/pyhwpx/core.html
"""
import pyhwpx
import os
import sys

# 콘솔 인코딩 설정
sys.stdout.reconfigure(encoding='utf-8')

def test_basic_document():
    """기본 문서 생성 및 저장"""
    print("=== pyhwpx 기본 문서 생성 테스트 ===\n")
    
    # HWP 문서 생성
    hwp = pyhwpx.Hwp()
    
    # 제목 작성
    hwp.insert_text("pyhwpx 테스트 문서")
    hwp.set_font(Height=20, Bold=True)
    hwp.BreakPara()  # 줄바꿈
    hwp.BreakPara()
    
    # 본문 작성
    hwp.set_font(Height=10, Bold=False)
    hwp.insert_text("이 문서는 pyhwpx를 사용하여 자동으로 생성되었습니다.")
    hwp.BreakPara()
    hwp.BreakPara()
    
    # 저장 경로 생성
    save_path = os.path.join("hwp", "basic_test.hwp")
    os.makedirs("hwp", exist_ok=True)
    
    # 문서 저장
    hwp.save(save_path)
    print(f"✓ 기본 문서가 생성되었습니다: {save_path}")
    
    hwp.quit()
    return save_path

def test_table_document():
    """표가 포함된 문서 생성"""
    print("\n=== 표 삽입 테스트 ===\n")
    
    hwp = pyhwpx.Hwp()
    
    # 제목
    hwp.insert_text("표 삽입 테스트")
    hwp.set_font(Height=16, Bold=True)
    hwp.BreakPara()
    hwp.BreakPara()
    
    # 본문
    hwp.set_font(Height=10, Bold=False)
    hwp.insert_text("아래는 3행 3열 표입니다:")
    hwp.BreakPara()
    
    # 표 생성
    hwp.create_table(rows=3, cols=3)
    
    save_path = os.path.join("hwp", "table_test.hwp")
    hwp.save(save_path)
    print(f"✓ 표 문서가 생성되었습니다: {save_path}")
    
    hwp.quit()
    return save_path

def test_formatting():
    """다양한 서식 테스트"""
    print("\n=== 서식 테스트 ===\n")
    
    hwp = pyhwpx.Hwp()
    
    # 제목
    hwp.insert_text("다양한 서식 테스트")
    hwp.set_font(Height=16, Bold=True, FaceName="맑은 고딕")
    hwp.BreakPara()
    hwp.BreakPara()
    
    # 볼드체
    hwp.set_font(Height=11, Bold=False)
    hwp.insert_text("1. 볼드체: ")
    hwp.set_font(Bold=True)
    hwp.insert_text("중요한 내용")
    hwp.set_font(Bold=False)
    hwp.BreakPara()
    
    # 이탤릭
    hwp.insert_text("2. 이탤릭: ")
    hwp.set_font(Italic=True)
    hwp.insert_text("강조된 내용")
    hwp.set_font(Italic=False)
    hwp.BreakPara()
    
    # 밑줄
    hwp.insert_text("3. 밑줄: ")
    hwp.set_font(UnderlineType=1)
    hwp.insert_text("밑줄 친 내용")
    hwp.set_font(UnderlineType=0)
    hwp.BreakPara()
    
    # 텍스트 색상
    hwp.insert_text("4. 텍스트 색상: ")
    hwp.set_font(TextColor=hwp.rgb_color(255, 0, 0))  # 빨간색
    hwp.insert_text("빨간 글자")
    hwp.set_font(TextColor=0xffffffff)  # 기본값으로 복원
    hwp.BreakPara()
    
    save_path = os.path.join("hwp", "formatting_test.hwp")
    hwp.save(save_path)
    print(f"✓ 서식 테스트 문서가 생성되었습니다: {save_path}")
    
    hwp.quit()
    return save_path

def test_read_document(file_path):
    """문서 읽기 테스트"""
    if not os.path.exists(file_path):
        print(f"⚠ 파일이 존재하지 않습니다: {file_path}")
        return
    
    print(f"\n=== 문서 읽기 테스트: {file_path} ===\n")
    
    hwp = pyhwpx.Hwp()
    hwp.open(file_path)
    
    # 텍스트 추출
    text = hwp.get_text()
    print("문서 내용:")
    print("-" * 50)
    print(text)
    print("-" * 50)
    
    hwp.quit()
    print("\n✓ 문서를 성공적으로 읽었습니다.")

def test_advanced_table():
    """고급 표 기능 테스트"""
    print("\n=== 고급 표 기능 테스트 ===\n")
    
    hwp = pyhwpx.Hwp()
    
    # 제목
    hwp.insert_text("성적표")
    hwp.set_font(Height=16, Bold=True)
    hwp.BreakPara()
    hwp.BreakPara()
    
    # 표 생성 (4행 4열)
    hwp.create_table(rows=4, cols=4)
    
    # 표 데이터 입력 (헤더)
    hwp.insert_text("이름")
    hwp.TableRightCell()  # 오른쪽 셀로 이동
    hwp.insert_text("수학")
    hwp.TableRightCell()
    hwp.insert_text("영어")
    hwp.TableRightCell()
    hwp.insert_text("과학")
    
    # 다음 행으로 이동
    hwp.TableLowerCell()
    hwp.TableLeftCell()
    hwp.TableLeftCell()
    hwp.TableLeftCell()
    
    # 데이터 입력
    hwp.insert_text("학생1")
    hwp.TableRightCell()
    hwp.insert_text("90")
    hwp.TableRightCell()
    hwp.insert_text("85")
    hwp.TableRightCell()
    hwp.insert_text("88")
    
    save_path = os.path.join("hwp", "advanced_table.hwp")
    hwp.save(save_path)
    print(f"✓ 고급 표 문서가 생성되었습니다: {save_path}")
    
    hwp.quit()
    return save_path

if __name__ == "__main__":
    try:
        # 기본 문서 생성
        doc1 = test_basic_document()
        
        # 표 문서 생성
        doc2 = test_table_document()
        
        # 서식 테스트
        doc3 = test_formatting()
        
        # 고급 표 기능
        doc4 = test_advanced_table()
        
        # 문서 읽기 테스트
        test_read_document(doc1)
        
        print("\n" + "="*50)
        print("✅ 모든 테스트가 완료되었습니다!")
        print("="*50)
        print(f"\n생성된 파일들:")
        print(f"  - {doc1}")
        print(f"  - {doc2}")
        print(f"  - {doc3}")
        print(f"  - {doc4}")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

