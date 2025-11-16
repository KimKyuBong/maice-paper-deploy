"""
pyhwpx 최소 테스트 - 문서 생성 및 저장 확인
"""
import pyhwpx
import os
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("HWP 객체 생성 중...")
hwp = pyhwpx.Hwp()
print("[OK] HWP 객체 생성 완료")

print("\n텍스트 입력 중...")
hwp.insert_text("테스트 문서입니다.")
print("[OK] 텍스트 입력 완료")

# 저장 경로
save_path = os.path.abspath(os.path.join("hwp", "minimal_test.hwp"))
os.makedirs("hwp", exist_ok=True)

print(f"\n문서 저장 중: {save_path}")
result = hwp.save(save_path)
print(f"저장 결과: {result}")

# 잠시 대기
time.sleep(1)

print("\nHWP 종료 중...")
hwp.quit()
print("[OK] HWP 종료 완료")

# 파일 존재 확인
time.sleep(1)
if os.path.exists(save_path):
    file_size = os.path.getsize(save_path)
    print(f"\n[SUCCESS] 파일이 성공적으로 생성되었습니다!")
    print(f"   경로: {save_path}")
    print(f"   크기: {file_size} bytes")
else:
    print(f"\n[ERROR] 파일이 생성되지 않았습니다: {save_path}")
    
    # HWP 프로세스 확인
    print("\n실행 중인 HWP 프로세스 확인:")
    os.system("tasklist | findstr /i hwp")

