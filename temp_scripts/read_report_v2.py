"""
report.hwpx 파일 상세 분석 - 다양한 방법으로 읽기
"""
import pyhwpx
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = os.path.abspath("hwp/report.hwpx")

print(f"파일 분석 중: {file_path}")
print("="*80)

try:
    hwp = pyhwpx.Hwp()
    hwp.open(file_path)
    
    print("\n📄 문서 기본 정보")
    print("="*80)
    print(f"페이지 수: {hwp.PageCount}")
    print(f"현재 페이지: {hwp.current_page}")
    
    # 방법 1: 첫 페이지로 이동 후 텍스트 읽기
    print("\n📖 방법 1: 첫 페이지 텍스트 읽기")
    print("="*80)
    hwp.goto_page(1)
    
    # 처음으로 이동
    hwp.Run("MoveDocBegin")
    
    # 선택하여 텍스트 가져오기
    hwp.Run("Select")
    hwp.Run("SelectAll")
    
    selected_text = hwp.get_selected_text()
    print(f"선택된 텍스트 타입: {type(selected_text)}")
    print(f"선택된 텍스트 길이: {len(str(selected_text))}")
    
    if selected_text:
        print("\n처음 1000자:")
        print("-"*80)
        print(str(selected_text)[:1000])
        print("-"*80)
    
    # 방법 2: 페이지별로 텍스트 읽기
    print("\n\n📖 방법 2: 각 페이지별 텍스트 확인 (처음 5페이지)")
    print("="*80)
    
    for page in range(1, min(6, hwp.PageCount + 1)):
        print(f"\n--- 페이지 {page} ---")
        page_text = hwp.get_page_text(page)
        print(f"타입: {type(page_text)}")
        if page_text and len(str(page_text)) > 0:
            preview = str(page_text)[:200].replace('\n', ' ')
            print(f"내용: {preview}...")
        else:
            print("(내용 없음 또는 읽기 실패)")
    
    # 방법 3: 텍스트 파일로 저장 시도
    print("\n\n💾 방법 3: 텍스트 파일로 내보내기")
    print("="*80)
    
    txt_path = "hwp/report_export.txt"
    result = hwp.get_text_file(txt_path)
    print(f"내보내기 결과: {result}")
    
    if os.path.exists(txt_path):
        file_size = os.path.getsize(txt_path)
        print(f"생성된 파일 크기: {file_size:,} bytes")
        
        if file_size > 0:
            with open(txt_path, 'r', encoding='utf-8') as f:
                content = f.read(2000)
                print(f"\n내보낸 파일 내용 (처음 2000자):")
                print("-"*80)
                print(content)
                print("-"*80)
    
    # 방법 4: 문서 구조 정보
    print("\n\n🔍 방법 4: 문서 구조 정보")
    print("="*80)
    
    # 표 찾기
    hwp.Run("MoveDocBegin")
    tables_found = 0
    try:
        # 표 컨트롤 찾기
        ctrl_list = hwp.ctrl_list
        print(f"컨트롤 리스트 타입: {type(ctrl_list)}")
    except Exception as e:
        print(f"컨트롤 리스트 확인 실패: {e}")
    
    print("\n문서 분석 완료!")
    
    hwp.quit()
    
except Exception as e:
    print(f"\n오류 발생: {e}")
    import traceback
    traceback.print_exc()

