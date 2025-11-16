"""
pyhwpx 문서 편집 실용 예제 모음
공식 문서: https://martiniifun.github.io/pyhwpx/core.html
"""
import pyhwpx
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')


def example_1_open_and_read(file_path):
    """예제 1: 문서 열기 및 전체 텍스트 읽기"""
    print("="*60)
    print("예제 1: 문서 열기 및 텍스트 읽기")
    print("="*60)
    
    hwp = pyhwpx.Hwp()
    hwp.open(file_path)
    
    # 전체 텍스트 가져오기
    text = hwp.get_text()
    print(f"\n문서 내용:\n{text}\n")
    
    hwp.quit()


def example_2_find_and_replace(file_path, find_text, replace_text):
    """예제 2: 찾아서 바꾸기"""
    print("="*60)
    print("예제 2: 찾아서 바꾸기")
    print("="*60)
    print(f"찾을 텍스트: '{find_text}' → 바꿀 텍스트: '{replace_text}'")
    
    hwp = pyhwpx.Hwp()
    hwp.open(file_path)
    
    # 전체 문서에서 찾아 바꾸기
    count = hwp.find_replace_all(find_text, replace_text)
    print(f"\n{count}개 항목을 변경했습니다.")
    
    # 새 이름으로 저장
    new_path = file_path.replace('.hwp', '_edited.hwp')
    hwp.save(new_path)
    print(f"저장 완료: {new_path}")
    
    hwp.quit()
    return new_path


def example_3_add_content_at_end(file_path, content_to_add):
    """예제 3: 문서 끝에 내용 추가"""
    print("="*60)
    print("예제 3: 문서 끝에 내용 추가")
    print("="*60)
    
    hwp = pyhwpx.Hwp()
    hwp.open(file_path)
    
    # 문서 끝으로 이동 (Ctrl+End)
    hwp.KeyDown("End", ctrl=True)
    
    # 새 줄 추가
    hwp.BreakPara()
    hwp.BreakPara()
    
    # 내용 추가
    hwp.insert_text("--- 추가된 내용 ---")
    hwp.BreakPara()
    hwp.insert_text(content_to_add)
    
    # 저장
    new_path = file_path.replace('.hwp', '_added.hwp')
    hwp.save(new_path)
    print(f"내용 추가 완료: {new_path}")
    
    hwp.quit()
    return new_path


def example_4_add_table(file_path):
    """예제 4: 문서에 표 추가"""
    print("="*60)
    print("예제 4: 문서에 표 추가")
    print("="*60)
    
    hwp = pyhwpx.Hwp()
    hwp.open(file_path)
    
    # 문서 끝으로 이동
    hwp.KeyDown("End", ctrl=True)
    hwp.BreakPara()
    hwp.BreakPara()
    
    # 표 제목
    hwp.insert_text("추가된 표:")
    hwp.BreakPara()
    
    # 3행 4열 표 생성
    hwp.create_table(rows=3, cols=4)
    
    # 저장
    new_path = file_path.replace('.hwp', '_with_table.hwp')
    hwp.save(new_path)
    print(f"표 추가 완료: {new_path}")
    
    hwp.quit()
    return new_path


def example_5_format_text(file_path, target_text):
    """예제 5: 특정 텍스트 찾아서 서식 변경"""
    print("="*60)
    print("예제 5: 특정 텍스트 서식 변경")
    print("="*60)
    print(f"서식 변경할 텍스트: '{target_text}'")
    
    hwp = pyhwpx.Hwp()
    hwp.open(file_path)
    
    # 텍스트 찾기
    if hwp.find(target_text):
        # 찾은 텍스트 선택
        hwp.SelectAll()  # 전체 선택 후
        hwp.find(target_text)  # 다시 찾으면 해당 텍스트가 선택됨
        
        # 서식 적용 (빨간색, 볼드, 크기 14)
        hwp.set_font(
            Bold=True,
            Height=14,
            TextColor=hwp.rgb_color(255, 0, 0)
        )
        print(f"'{target_text}' 텍스트에 서식을 적용했습니다.")
    else:
        print(f"'{target_text}' 텍스트를 찾지 못했습니다.")
    
    # 저장
    new_path = file_path.replace('.hwp', '_formatted.hwp')
    hwp.save(new_path)
    print(f"저장 완료: {new_path}")
    
    hwp.quit()
    return new_path


def example_6_create_sample_doc():
    """예제 6: 테스트용 샘플 문서 생성"""
    print("="*60)
    print("예제 6: 샘플 문서 생성")
    print("="*60)
    
    hwp = pyhwpx.Hwp()
    
    # 제목
    hwp.insert_text("샘플 문서")
    hwp.set_font(Height=16, Bold=True)
    hwp.BreakPara()
    hwp.BreakPara()
    
    # 본문
    hwp.set_font(Height=10, Bold=False)
    hwp.insert_text("이것은 테스트용 샘플 문서입니다.")
    hwp.BreakPara()
    hwp.insert_text("여기서 '테스트' 라는 단어를 찾아 바꿀 수 있습니다.")
    hwp.BreakPara()
    hwp.BreakPara()
    
    # 리스트
    hwp.insert_text("1. 첫 번째 항목")
    hwp.BreakPara()
    hwp.insert_text("2. 두 번째 항목")
    hwp.BreakPara()
    hwp.insert_text("3. 세 번째 항목")
    
    # 저장
    save_path = os.path.join("hwp", "sample_document.hwp")
    os.makedirs("hwp", exist_ok=True)
    hwp.save(save_path)
    print(f"샘플 문서 생성 완료: {save_path}")
    
    hwp.quit()
    return save_path


def example_7_get_document_info(file_path):
    """예제 7: 문서 정보 가져오기"""
    print("="*60)
    print("예제 7: 문서 정보 확인")
    print("="*60)
    
    hwp = pyhwpx.Hwp()
    hwp.open(file_path)
    
    # 문서 정보
    print(f"문서 경로: {hwp.Path}")
    print(f"페이지 수: {hwp.PageCount}")
    print(f"수정됨: {hwp.is_modified}")
    print(f"비어있음: {hwp.is_empty}")
    
    hwp.quit()


# 메인 실행 예제
if __name__ == "__main__":
    print("\n*** pyhwpx 문서 편집 예제 시연 ***\n")
    
    # 1. 샘플 문서 생성
    sample_file = example_6_create_sample_doc()
    
    print("\n" + "="*60)
    input("샘플 문서가 생성되었습니다. 계속하려면 Enter를 누르세요...")
    
    # 2. 문서 읽기
    example_1_open_and_read(sample_file)
    
    # 3. 찾아 바꾸기
    example_2_find_and_replace(sample_file, "테스트", "실전")
    
    # 4. 내용 추가
    example_3_add_content_at_end(sample_file, "이 내용은 문서 끝에 추가되었습니다.")
    
    # 5. 표 추가
    example_4_add_table(sample_file)
    
    # 6. 서식 변경
    example_5_format_text(sample_file, "샘플 문서")
    
    # 7. 문서 정보
    example_7_get_document_info(sample_file)
    
    print("\n" + "="*60)
    print("모든 예제 실행 완료!")
    print("hwp 폴더에서 생성된 파일들을 확인하세요.")
    print("="*60)

