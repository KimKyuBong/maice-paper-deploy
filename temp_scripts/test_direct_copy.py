"""
원본 이미지 XML을 직접 복사해서 테스트
"""
import sys
import zipfile
import shutil
import os

sys.stdout.reconfigure(encoding='utf-8')

# 원본 파일
original = "hwp/report_backup_20251112_020239.hwpx"
test_file = "hwp/test_diagram_direct.hwpx"

# 복사
shutil.copy2(original, test_file)

# 압축 해제
temp_dir = "hwp/temp_direct"
if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)

with zipfile.ZipFile(test_file, 'r') as zf:
    zf.extractall(temp_dir)

# 1. diagram100.PNG 복사
shutil.copy2(
    "docs/diagrams/output/png/figure3-2-architecture.png",
    os.path.join(temp_dir, "BinData", "diagram100.PNG")
)

# 2. section2.xml 수정 - 첫 이미지 XML 찾아서 복사
with open(os.path.join(temp_dir, "Contents", "section2.xml"), 'r', encoding='utf-8') as f:
    xml = f.read()

# 첫 번째 <hp:pic>를 포함한 전체 문단 추출
pic_start = xml.find('<hp:pic ')
p_start = xml.rfind('<hp:p ', 0, pic_start)
p_end = xml.find('</hp:p>', pic_start) + len('</hp:p>')

original_para = xml[p_start:p_end]

print("="*80)
print("원본 이미지 문단 추출:")
print("="*80)
print(original_para[:500])

# image1을 diagram100으로 교체
new_para = original_para.replace('binaryItemIDRef="image1"', 'binaryItemIDRef="diagram100"')

# XML의 첫 번째 문단 앞에 추가
first_p = xml.find('<hp:p')
new_xml = xml[:first_p] + new_para + '\n' + xml[first_p:]

with open(os.path.join(temp_dir, "Contents", "section2.xml"), 'w', encoding='utf-8') as f:
    f.write(new_xml)

print(f"\n✓ section2.xml 수정 완료")

# 재압축
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

print(f"✓ 재압축 완료: {test_file}")

# 정리
shutil.rmtree(temp_dir)

print("\n" + "="*80)
print(f"테스트 파일: {test_file}")
print("="*80)
print("\n원본 이미지 XML을 완전히 복사한 버전입니다.")
print("이 파일을 열어서 맨 앞에 추가된 이미지(PNG 컬러)가 보이는지 확인하세요!")

