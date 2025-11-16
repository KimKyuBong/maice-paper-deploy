"""
report.hwpx 파일 읽기
"""
import pyhwpx
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = os.path.abspath("hwp/report.hwpx")

print(f"파일 읽기 중: {file_path}")
print("="*80)

if not os.path.exists(file_path):
    print(f"파일이 존재하지 않습니다: {file_path}")
    sys.exit(1)

print(f"파일 크기: {os.path.getsize(file_path):,} bytes")
print()

try:
    hwp = pyhwpx.Hwp()
    hwp.open(file_path)
    
    # 문서 정보
    print("=" * 80)
    print("📄 문서 정보")
    print("=" * 80)
    print(f"경로: {hwp.Path}")
    print(f"페이지 수: {hwp.PageCount}")
    print(f"현재 페이지: {hwp.current_page}")
    print(f"수정됨: {hwp.is_modified}")
    print(f"비어있음: {hwp.is_empty}")
    
    # 전체 텍스트 가져오기
    print("\n" + "=" * 80)
    print("📝 문서 내용 (처음 2000자)")
    print("=" * 80)
    text = hwp.get_text()
    print(text[:2000])
    
    if len(text) > 2000:
        print(f"\n... (총 {len(text):,}자 중 처음 2000자만 표시)")
    
    print("\n" + "=" * 80)
    print(f"전체 텍스트 길이: {len(text):,}자")
    print("=" * 80)
    
    # 문서를 저장하여 txt로 내보내기
    txt_output = "hwp/report_content.txt"
    with open(txt_output, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"\n전체 내용을 텍스트 파일로 저장했습니다: {txt_output}")
    
    hwp.quit()
    
except Exception as e:
    print(f"\n오류 발생: {e}")
    import traceback
    traceback.print_exc()

