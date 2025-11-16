"""
원본 파일의 첫 이미지만 교체 테스트
"""
import sys
import os
import zipfile
import shutil
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("단일 이미지 교체 테스트")
print("="*80)

# 1. 원본 복사
original = "hwp/report_backup_20251112_020239.hwpx"
test_file = "hwp/test_single_image.hwpx"

shutil.copy2(original, test_file)
print(f"✓ 원본 복사: {test_file}")

# 2. HWPX 압축 해제
temp_dir = "hwp/temp_test"
if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)

with zipfile.ZipFile(test_file, 'r') as zf:
    zf.extractall(temp_dir)

print(f"✓ 압축 해제: {temp_dir}")

# 3. 첫 번째 이미지 교체 (image1.BMP)
# PNG를 BMP로 변환
png_file = "docs/diagrams/output/png/figure3-1-pipeline.png"
img = Image.open(png_file)

if img.mode == 'RGBA':
    background = Image.new('RGB', img.size, (255, 255, 255))
    background.paste(img, mask=img.split()[3])
    img = background
elif img.mode != 'RGB':
    img = img.convert('RGB')

# image1.BMP로 저장
bmp_path = os.path.join(temp_dir, "BinData", "image1.BMP")
img.save(bmp_path, 'BMP')

print(f"✓ 이미지 교체: image1.BMP ({os.path.getsize(bmp_path):,} bytes)")

# 4. 재압축
os.remove(test_file)

# mimetype 먼저
with zipfile.ZipFile(test_file, 'w', zipfile.ZIP_STORED) as zf:
    mimetype_path = os.path.join(temp_dir, 'mimetype')
    if os.path.exists(mimetype_path):
        zf.write(mimetype_path, 'mimetype')

# 나머지 파일
with zipfile.ZipFile(test_file, 'a', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            if file == 'mimetype':
                continue
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, temp_dir)
            zf.write(file_path, arcname)

print(f"✓ 재압축 완료: {test_file}")
print(f"✓ 파일 크기: {os.path.getsize(test_file):,} bytes")

# 정리
shutil.rmtree(temp_dir)

print("\n" + "="*80)
print(f"테스트 파일 생성 완료: {test_file}")
print("="*80)
print("\n이 파일을 열어서 첫 번째 이미지가 보이는지 확인하세요!")
print("보인다면 → 이미지 파일 자체는 문제없음, XML 구조 문제")
print("안 보인다면 → 이미지 파일 또는 한글 프로그램 문제")

