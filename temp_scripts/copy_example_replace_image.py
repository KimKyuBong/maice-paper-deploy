"""
example.hwpx 복사 → 이미지만 교체
"""
import sys
import zipfile
import shutil
import os
import hashlib
import base64

sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("example.hwpx 이미지만 교체")
print("="*80)

# example.hwpx 복사
example = "hwp/example.hwpx"
temp_dir = "hwp/temp_example_copy"

if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)

with zipfile.ZipFile(example, 'r') as zf:
    zf.extractall(temp_dir)

print("✓ example.hwpx 압축 해제")

# 기존 image1.png 삭제
old_image = os.path.join(temp_dir, "BinData", "image1.png")
if os.path.exists(old_image):
    os.remove(old_image)
    print("✓ 기존 image1.png 삭제")

# 새 PNG 복사
new_png = "docs/diagrams/output/png/figure3-1-pipeline.png"
new_image = os.path.join(temp_dir, "BinData", "image1.png")
shutil.copy2(new_png, new_image)

print(f"✓ 새 이미지 복사: {new_png}")
print(f"  → BinData/image1.png")

# hashkey 계산
with open(new_image, 'rb') as f:
    data = f.read()
    hash_md5 = hashlib.md5(data).digest()
    hashkey = base64.b64encode(hash_md5).decode('ascii')

print(f"  hashkey: {hashkey}")

# content.hpf 업데이트
hpf_path = os.path.join(temp_dir, "Contents", "content.hpf")
with open(hpf_path, 'r', encoding='utf-8') as f:
    hpf = f.read()

# hashkey 교체
import re
hpf = re.sub(r'(<opf:item id="image1"[^>]*hashkey=")[^"]*(")', rf'\g<1>{hashkey}\g<2>', hpf)

with open(hpf_path, 'w', encoding='utf-8') as f:
    f.write(hpf)

print("✓ content.hpf hashkey 업데이트")

# 재압축
output = "hwp/SIMPLE_ONE_IMAGE.hwpx"
if os.path.exists(output):
    os.remove(output)

with zipfile.ZipFile(output, 'w', zipfile.ZIP_STORED) as zf:
    mimetype = os.path.join(temp_dir, 'mimetype')
    if os.path.exists(mimetype):
        zf.write(mimetype, 'mimetype')

with zipfile.ZipFile(output, 'a', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            if file == 'mimetype':
                continue
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, temp_dir)
            zf.write(file_path, arcname)

print(f"\n✓ 생성: {output} ({os.path.getsize(output):,} bytes)")

shutil.rmtree(temp_dir)

print("\n" + "="*80)
print("📌 hwp/SIMPLE_ONE_IMAGE.hwpx")
print("="*80)
print("\n✅ example.hwpx 복사")
print("✅ image1.png만 교체 (figure3-1-pipeline)")
print("✅ hashkey 업데이트")
print("\n→ 이 파일 열어서 컬러 이미지 1개 확인!")

