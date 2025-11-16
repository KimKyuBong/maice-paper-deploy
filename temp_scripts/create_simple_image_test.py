"""
빈 HWPX에 이미지 하나만 테스트
"""
import sys
import zipfile
import shutil
import os
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("빈 HWPX + 이미지 1개 테스트")
print("="*80)

# 원본에서 구조만 가져오기
original = "hwp/report_backup_20251112_020239.hwpx"
temp_dir = "hwp/temp_simple"

if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)

with zipfile.ZipFile(original, 'r') as zf:
    zf.extractall(temp_dir)

# 1. BinData 폴더 비우기
bindata_dir = os.path.join(temp_dir, "BinData")
for f in os.listdir(bindata_dir):
    os.remove(os.path.join(bindata_dir, f))

print("✓ BinData 폴더 비움")

# 2. 이미지 1개만 추가
png_file = "docs/diagrams/output/png/figure3-1-pipeline.png"
img = Image.open(png_file)

# BMP로 변환
if img.mode == 'RGBA':
    background = Image.new('RGB', img.size, (255, 255, 255))
    background.paste(img, mask=img.split()[3])
    img = background
elif img.mode != 'RGB':
    img = img.convert('RGB')

# image1.BMP로 저장
bmp_path = os.path.join(bindata_dir, "image1.BMP")
img.save(bmp_path, 'BMP')

print(f"✓ 이미지 추가: image1.BMP ({os.path.getsize(bmp_path):,} bytes)")

# 3. section2.xml을 아주 간단하게 - 이미지 1개만
simple_section = '''<?xml version="1.0" encoding="UTF-8" standalone="yes" ?><hs:sec xmlns:ha="http://www.hancom.co.kr/hwpml/2011/app" xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph" xmlns:hp10="http://www.hancom.co.kr/hwpml/2016/paragraph" xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section" xmlns:hc="http://www.hancom.co.kr/hwpml/2011/core" xmlns:hh="http://www.hancom.co.kr/hwpml/2011/head" xmlns:hhs="http://www.hancom.co.kr/hwpml/2011/history" xmlns:hm="http://www.hancom.co.kr/hwpml/2011/master-page" xmlns:hpf="http://www.hancom.co.kr/schema/2011/hpf" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf/" xmlns:ooxmlchart="http://www.hancom.co.kr/hwpml/2016/ooxmlchart" xmlns:hwpunitchar="http://www.hancom.co.kr/hwpml/2016/HwpUnitChar" xmlns:epub="http://www.idpf.org/2007/ops" xmlns:config="urn:oasis:names:tc:opendocument:xmlns:config:1.0" xml:id="defaultIdValue"><hp:secPr><hp:startNum pageStartsOn="BOTH" page="0" pic="0" tbl="0" equation="0"/><hp:pageGap/><hp:pagePr textWidth="43936" textHeight="60416" gutterType="LEFT_ONLY"><hp:margin left="7087" right="7087" top="5668" bottom="4252" header="4252" footer="4252" gutter="0"/></hp:pagePr></hp:secPr>
<hp:p id="0" paraPrIDRef="17" styleIDRef="12" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="4"><hp:t>테스트: 이미지가 아래에 표시되어야 합니다.</hp:t></hp:run></hp:p>
<hp:p id="0" paraPrIDRef="37" styleIDRef="12" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="4"><hp:pic id="2001261736" zOrder="10" numberingType="PICTURE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" href="" groupLevel="0" instid="927519913" reverse="0"><hp:offset x="0" y="0"/><hp:orgSz width="50100" height="42840"/><hp:curSz width="35718" height="30547"/><hp:flip horizontal="0" vertical="0"/><hp:rotationInfo angle="0" centerX="17859" centerY="15273" rotateimage="1"/><hp:renderingInfo><hc:transMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/><hc:scaMatrix e1="0.712934" e2="0" e3="0" e4="0" e5="0.713049" e6="0"/><hc:rotMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/></hp:renderingInfo><hc:img binaryItemIDRef="image1" bright="0" contrast="0" effect="REAL_PIC" alpha="0"/><hp:imgRect><hc:pt0 x="0" y="0"/><hc:pt1 x="50100" y="0"/><hc:pt2 x="50100" y="42840"/><hc:pt3 x="0" y="42840"/></hp:imgRect><hp:imgClip left="0" right="50100" top="0" bottom="42840"/><hp:inMargin left="0" right="0" top="0" bottom="0"/><hp:imgDim dimwidth="50100" dimheight="42840"/><hp:effects/><hp:sz width="35718" widthRelTo="ABSOLUTE" height="30547" heightRelTo="ABSOLUTE" protect="0"/><hp:pos treatAsChar="0" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="COLUMN" vertAlign="TOP" horzAlign="LEFT" vertOffset="1765" horzOffset="4764"/><hp:outMargin left="0" right="0" top="0" bottom="0"/></hp:pic><hp:t/></hp:run><hp:linesegarray><hp:lineseg textpos="0" vertpos="6440" vertsize="1100" textheight="1100" baseline="935" spacing="880" horzpos="0" horzsize="43936" flags="1441792"/></hp:linesegarray></hp:p>
</hs:sec>'''

section2_path = os.path.join(temp_dir, "Contents", "section2.xml")
with open(section2_path, 'w', encoding='utf-8') as f:
    f.write(simple_section)

print("✓ section2.xml을 간단한 테스트 버전으로 교체")

# 4. 재압축
test_file = "hwp/SIMPLE_IMAGE_TEST.hwpx"
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
print(f"  파일 크기: {os.path.getsize(test_file):,} bytes")

shutil.rmtree(temp_dir)

print("\n" + "="*80)
print("테스트 파일: hwp/SIMPLE_IMAGE_TEST.hwpx")
print("="*80)
print("\n내용:")
print("  - 1페이지 1줄: '테스트: 이미지가 아래에 표시되어야 합니다.'")
print("  - 이미지 1개: figure3-1-pipeline (컬러)")
print("\n→ 이 파일을 열어서 이미지가 보이는지 확인하세요!")
print("   보이면 성공, 안 보이면 추가 디버깅 필요")

