"""
content.hpf 업데이트 - 간단한 버전
"""
import sys
import zipfile
import shutil
import os
import hashlib
import base64

sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("content.hpf 업데이트")
print("="*80)

# 원본 복사
original = "hwp/report_backup_20251112_020239.hwpx"
temp_dir = "hwp/temp_hpf_simple"

if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)

with zipfile.ZipFile(original, 'r') as zf:
    zf.extractall(temp_dir)

# BinData 비우기
bindata_dir = os.path.join(temp_dir, "BinData")
for f in os.listdir(bindata_dir):
    os.remove(os.path.join(bindata_dir, f))

# PNG 복사 (소문자)
png_file = "docs/diagrams/output/png/figure3-1-pipeline.png"
png_dest = os.path.join(bindata_dir, "image1.png")
shutil.copy2(png_file, png_dest)

# 해시 계산
with open(png_dest, 'rb') as f:
    data = f.read()
    hash_md5 = hashlib.md5(data).digest()
    hashkey = base64.b64encode(hash_md5).decode('ascii')

print(f"✓ PNG 복사: image1.png")
print(f"  hashkey: {hashkey}")

# content.hpf 수정
hpf_path = os.path.join(temp_dir, "Contents", "content.hpf")
with open(hpf_path, 'r', encoding='utf-8') as f:
    hpf = f.read()

import re
# 기존 이미지 항목 제거
hpf = re.sub(r'<opf:item id="image\d+"[^/]*/>', '', hpf)
# BinData 항목 제거
hpf = re.sub(r'<opf:item id="BIN\d+"[^/]*/>', '', hpf)

# 새 이미지 등록
new_item = f'<opf:item id="image1" href="BinData/image1.png" media-type="image/png" isEmbeded="1" hashkey="{hashkey}"/>'

manifest_end = hpf.find('</opf:manifest>')
hpf = hpf[:manifest_end] + new_item + hpf[manifest_end:]

with open(hpf_path, 'w', encoding='utf-8') as f:
    f.write(hpf)

print("✓ content.hpf 업데이트 완료")

# section0.xml을 example에서 복사
shutil.copy2(
    'hwp/example_extracted/Contents/section0.xml',
    os.path.join(temp_dir, "Contents", "section0.xml")
)

print("✓ section0.xml 복사")

# section2.xml 비우기  
section2_path = os.path.join(temp_dir, "Contents", "section2.xml")
with open(section2_path, 'r', encoding='utf-8') as f:
    s2 = f.read()

header_end = s2.find('<hp:p')
s2_empty = s2[:header_end] + '</hs:sec>'

with open(section2_path, 'w', encoding='utf-8') as f:
    f.write(s2_empty)

print("✓ section2.xml 비움")

# 재압축
test_file = "hwp/TEST_HPF_FIXED.hwpx"
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

print(f"\n✓ 생성: {test_file} ({os.path.getsize(test_file):,} bytes)")

shutil.rmtree(temp_dir)

print("\n" + "="*80)
print("📌 hwp/TEST_HPF_FIXED.hwpx")
print("="*80)
print("\n✅ content.hpf에 image1.png 등록")
print("✅ PNG 파일 (소문자 .png)")
print("✅ hashkey 계산하여 등록")
print("\n→ 이 파일 열어서 이미지 확인!")

