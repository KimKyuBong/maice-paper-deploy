"""
다양한 파일명 형식 테스트
"""
import sys
import zipfile
import shutil
import os
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

# 원본
original = "hwp/report_backup_20251112_020239.hwpx"
temp_dir = "hwp/temp_naming_test"

if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)

with zipfile.ZipFile(original, 'r') as zf:
    zf.extractall(temp_dir)

# PNG를 BMP로 변환 (test_single_image와 동일한 방식)
png_file = "docs/diagrams/output/png/figure3-2-architecture.png"
img = Image.open(png_file)

if img.mode == 'RGBA':
    background = Image.new('RGB', img.size, (255, 255, 255))
    background.paste(img, mask=img.split()[3])
    img = background
elif img.mode != 'RGB':
    img = img.convert('RGB')

# image39.BMP로 저장 (기존 시리즈 이어서)
bmp_path = os.path.join(temp_dir, "BinData", "image39.BMP")
img.save(bmp_path, 'BMP')

print(f"✓ 이미지 저장: image39.BMP ({os.path.getsize(bmp_path):,} bytes)")

# section2.xml 수정 - 첫 이미지 복사
with open(os.path.join(temp_dir, "Contents", "section2.xml"), 'r', encoding='utf-8') as f:
    xml = f.read()

# 첫 이미지 문단 추출
pic_start = xml.find('<hp:pic ')
p_start = xml.rfind('<hp:p ', 0, pic_start)
p_end = xml.find('</hp:p>', pic_start) + len('</hp:p>')
original_para = xml[p_start:p_end]

# image1 → image39로 교체
new_para = original_para.replace('binaryItemIDRef="image1"', 'binaryItemIDRef="image39"')

# 문서 맨 앞에 추가
first_p = xml.find('<hp:p')
new_xml = xml[:first_p] + new_para + '\n' + xml[first_p:]

with open(os.path.join(temp_dir, "Contents", "section2.xml"), 'w', encoding='utf-8') as f:
    f.write(new_xml)

# 재압축
test_file = "hwp/test_image39.hwpx"
if os.path.exists(test_file):
    os.remove(test_file)

with zipfile.ZipFile(test_file, 'w', zipfile.ZIP_STORED) as zf:
    mimetype_path = os.path.join(temp_dir, 'mimetype')
    if os.path.exists(mimetype_path):
        zf.write(mimetype_path, 'mimetype')

with zipfile.ZipFile(test_file, 'a', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            if file == 'mimetype':
                continue
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, temp_dir)
            zf.write(file_path, arcname)

print(f"✓ 생성 완료: {test_file}")

shutil.rmtree(temp_dir)

print("\n" + "="*80)
print("테스트 파일:")
print("  hwp/test_image39.hwpx")
print("="*80)
print("\n✓ 기존 image 시리즈 이름 사용 (image39.BMP)")
print("✓ 원본 XML 완전히 복사")
print("\n이 파일을 열어서 맨 앞에 컬러 이미지가 보이는지 확인하세요!")

