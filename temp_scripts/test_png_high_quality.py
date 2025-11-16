"""
PNG 고품질 삽입 테스트
"""
import sys
import zipfile
import shutil
import os
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("PNG 고품질 삽입 테스트")
print("="*80)

# 원본 복사
original = "hwp/report_backup_20251112_020239.hwpx"
temp_dir = "hwp/temp_png_test"

if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)

with zipfile.ZipFile(original, 'r') as zf:
    zf.extractall(temp_dir)

# BinData 비우기
bindata_dir = os.path.join(temp_dir, "BinData")
for f in os.listdir(bindata_dir):
    os.remove(os.path.join(bindata_dir, f))

# PNG 그대로 복사 (변환 없음!)
png_file = "docs/diagrams/output/png/figure3-1-pipeline.png"
img = Image.open(png_file)

# PNG 그대로 저장
png_dest = os.path.join(bindata_dir, "image1.PNG")
shutil.copy2(png_file, png_dest)

print(f"✓ PNG 복사: image1.PNG")
print(f"  원본 크기: {img.size}")
print(f"  모드: {img.mode}")

# HWP 크기 계산
width_px, height_px = img.size
dpi = img.info.get('dpi', (96, 96))[0]

# HWP units 변환 (1 inch = 7200 HWP units)
width_hwp = int(width_px / dpi * 7200)
height_hwp = int(height_px / dpi * 7200)

print(f"  HWP 크기: {width_hwp} x {height_hwp}")

# 적절한 표시 크기 (A4 너비의 70% 정도)
max_width = 80000  # 더 작게
if width_hwp > max_width:
    scale = max_width / width_hwp
    cur_width = max_width
    cur_height = int(height_hwp * scale)
else:
    cur_width = width_hwp
    cur_height = height_hwp

print(f"  표시 크기: {cur_width} x {cur_height}")

# 스케일 계산
scale_x = cur_width / width_hwp
scale_y = cur_height / height_hwp

print(f"  스케일: {scale_x:.6f}, {scale_y:.6f}")

# section2.xml 생성
simple_section = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes" ?><hs:sec xmlns:ha="http://www.hancom.co.kr/hwpml/2011/app" xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph" xmlns:hp10="http://www.hancom.co.kr/hwpml/2016/paragraph" xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section" xmlns:hc="http://www.hancom.co.kr/hwpml/2011/core" xmlns:hh="http://www.hancom.co.kr/hwpml/2011/head" xmlns:hhs="http://www.hancom.co.kr/hwpml/2011/history" xmlns:hm="http://www.hancom.co.kr/hwpml/2011/master-page" xmlns:hpf="http://www.hancom.co.kr/schema/2011/hpf" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf/" xmlns:ooxmlchart="http://www.hancom.co.kr/hwpml/2016/ooxmlchart" xmlns:hwpunitchar="http://www.hancom.co.kr/hwpml/2016/HwpUnitChar" xmlns:epub="http://www.idpf.org/2007/ops" xmlns:config="urn:oasis:names:tc:opendocument:xmlns:config:1.0" xml:id="defaultIdValue"><hp:secPr><hp:startNum pageStartsOn="BOTH" page="0" pic="0" tbl="0" equation="0"/><hp:pageGap/><hp:pagePr textWidth="43936" textHeight="60416" gutterType="LEFT_ONLY"><hp:margin left="7087" right="7087" top="5668" bottom="4252" header="4252" footer="4252" gutter="0"/></hp:pagePr></hp:secPr>
<hp:p id="0" paraPrIDRef="17" styleIDRef="12" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="4"><hp:t>PNG 고품질 테스트 - 컬러 이미지가 아래에 적절한 크기로 표시되어야 합니다.</hp:t></hp:run></hp:p>
<hp:p id="0" paraPrIDRef="37" styleIDRef="12" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="4"><hp:pic id="2001261736" zOrder="10" numberingType="PICTURE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" href="" groupLevel="0" instid="927519913" reverse="0"><hp:offset x="0" y="0"/><hp:orgSz width="{width_hwp}" height="{height_hwp}"/><hp:curSz width="{cur_width}" height="{cur_height}"/><hp:flip horizontal="0" vertical="0"/><hp:rotationInfo angle="0" centerX="{cur_width//2}" centerY="{cur_height//2}" rotateimage="1"/><hp:renderingInfo><hc:transMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/><hc:scaMatrix e1="{scale_x}" e2="0" e3="0" e4="0" e5="{scale_y}" e6="0"/><hc:rotMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/></hp:renderingInfo><hc:img binaryItemIDRef="image1" bright="0" contrast="0" effect="REAL_PIC" alpha="0"/><hp:imgRect><hc:pt0 x="0" y="0"/><hc:pt1 x="{width_hwp}" y="0"/><hc:pt2 x="{width_hwp}" y="{height_hwp}"/><hc:pt3 x="0" y="{height_hwp}"/></hp:imgRect><hp:imgClip left="0" right="{width_hwp}" top="0" bottom="{height_hwp}"/><hp:inMargin left="0" right="0" top="0" bottom="0"/><hp:imgDim dimwidth="{width_hwp}" dimheight="{height_hwp}"/><hp:effects/><hp:sz width="{cur_width}" widthRelTo="ABSOLUTE" height="{cur_height}" heightRelTo="ABSOLUTE" protect="0"/><hp:pos treatAsChar="0" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="COLUMN" vertAlign="TOP" horzAlign="LEFT" vertOffset="1765" horzOffset="4764"/><hp:outMargin left="0" right="0" top="0" bottom="0"/></hp:pic><hp:t/></hp:run><hp:linesegarray><hp:lineseg textpos="0" vertpos="6440" vertsize="1100" textheight="1100" baseline="935" spacing="880" horzpos="0" horzsize="43936" flags="1441792"/></hp:linesegarray></hp:p>
</hs:sec>'''

section2_path = os.path.join(temp_dir, "Contents", "section2.xml")
with open(section2_path, 'w', encoding='utf-8') as f:
    f.write(simple_section)

print("✓ section2.xml 생성 (PNG용 크기 조정)")

# 재압축
test_file = "hwp/PNG_HIGH_QUALITY_TEST.hwpx"
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

print(f"✓ 생성: {test_file} ({os.path.getsize(test_file):,} bytes)")

shutil.rmtree(temp_dir)

print("\n" + "="*80)
print("📌 테스트 파일: hwp/PNG_HIGH_QUALITY_TEST.hwpx")
print("="*80)
print("\n✓ PNG 원본 그대로 (변환 없음)")
print("✓ 크기 비율 계산하여 적용")
print("✓ 스케일 매트릭스 정확히 계산")
print("\n→ 이 파일 열어서 컬러 + 정상 비율 확인!")

