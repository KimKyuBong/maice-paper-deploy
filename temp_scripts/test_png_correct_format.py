"""
example.hwpx 방식 그대로 PNG 삽입
"""
import sys
import zipfile
import shutil
import os
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("PNG 삽입 (example.hwpx 방식)")
print("="*80)

# 원본
original = "hwp/report_backup_20251112_020239.hwpx"
temp_dir = "hwp/temp_png_correct"

if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)

with zipfile.ZipFile(original, 'r') as zf:
    zf.extractall(temp_dir)

# BinData 비우기
bindata_dir = os.path.join(temp_dir, "BinData")
for f in os.listdir(bindata_dir):
    os.remove(os.path.join(bindata_dir, f))

# PNG 복사 (소문자!)
png_file = "docs/diagrams/output/png/figure3-1-pipeline.png"
img = Image.open(png_file)

png_dest = os.path.join(bindata_dir, "image1.png")  # 소문자!
shutil.copy2(png_file, png_dest)

print(f"✓ PNG 복사: image1.png (소문자)")
print(f"  크기: {img.size}")

# 크기 계산
width_px, height_px = img.size
dpi = img.info.get('dpi', (96, 96))[0]

# 원본 이미지 크기 (HWP units)
img_width_hwp = int(width_px / dpi * 7200)
img_height_hwp = int(height_px / dpi * 7200)

# 표시 크기 (적절하게 조정)
max_width = 80000
if img_width_hwp > max_width:
    scale = max_width / img_width_hwp
    display_width = max_width
    display_height = int(img_height_hwp * scale)
else:
    display_width = img_width_hwp
    display_height = img_height_hwp

print(f"  원본 크기 (HWP): {img_width_hwp} x {img_height_hwp}")
print(f"  표시 크기 (HWP): {display_width} x {display_height}")

# 스케일
scale_x = display_width / img_width_hwp
scale_y = display_height / img_height_hwp

print(f"  스케일: {scale_x:.6f}, {scale_y:.6f}")

# section0.xml 생성 (example.hwpx 방식)
section_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes" ?><hs:sec xmlns:ha="http://www.hancom.co.kr/hwpml/2011/app" xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph" xmlns:hp10="http://www.hancom.co.kr/hwpml/2016/paragraph" xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section" xmlns:hc="http://www.hancom.co.kr/hwpml/2011/core" xmlns:hh="http://www.hancom.co.kr/hwpml/2011/head" xmlns:hhs="http://www.hancom.co.kr/hwpml/2011/history" xmlns:hm="http://www.hancom.co.kr/hwpml/2011/master-page" xmlns:hpf="http://www.hancom.co.kr/schema/2011/hpf" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf/" xmlns:ooxmlchart="http://www.hancom.co.kr/hwpml/2016/ooxmlchart" xmlns:hwpunitchar="http://www.hancom.co.kr/hwpml/2016/HwpUnitChar" xmlns:epub="http://www.idpf.org/2007/ops" xmlns:config="urn:oasis:names:tc:opendocument:xmlns:config:1.0"><hp:p id="3121190098" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="0"><hp:secPr id="" textDirection="HORIZONTAL" spaceColumns="1134" tabStop="8000" tabStopVal="4000" tabStopUnit="HWPUNIT" outlineShapeIDRef="1" memoShapeIDRef="1" textVerticalWidthHead="0" masterPageCnt="0"><hp:grid lineGrid="0" charGrid="0" wonggojiFormat="0"/><hp:startNum pageStartsOn="BOTH" page="0" pic="0" tbl="0" equation="0"/><hp:visibility hideFirstHeader="0" hideFirstFooter="0" hideFirstMasterPage="0" border="SHOW_ALL" fill="SHOW_ALL" hideFirstPageNum="0" hideFirstEmptyLine="0" showLineNumber="0" lineNumberShape restartType="0" countBy="0" distance="0" startNumber="0"/><hp:lineNumberShape restartType="0" countBy="0" distance="0" startNumber="0"/><hp:pagePr landscape="WIDELY" width="59528" height="84186" gutterType="LEFT_ONLY"><hp:margin header="4252" footer="4252" gutter="0" left="8504" right="8504" top="5668" bottom="4252"/></hp:pagePr><hp:footNotePr><hp:autoNumFormat type="DIGIT" userChar="" prefixChar="" suffixChar=")" supscript="0"/><hp:noteLine length="-1" type="SOLID" width="0.12 mm" color="#000000"/><hp:noteSpacing betweenNotes="283" belowLine="567" aboveLine="850"/><hp:numbering type="CONTINUOUS" newNum="1"/><hp:placement place="EACH_COLUMN" beneathText="0"/></hp:footNotePr><hp:endNotePr><hp:autoNumFormat type="DIGIT" userChar="" prefixChar="" suffixChar=")" supscript="0"/><hp:noteLine length="14692344" type="SOLID" width="0.12 mm" color="#000000"/><hp:noteSpacing betweenNotes="0" belowLine="567" aboveLine="850"/><hp:numbering type="CONTINUOUS" newNum="1"/><hp:placement place="END_OF_DOCUMENT" beneathText="0"/></hp:endNotePr><hp:pageBorderFill type="BOTH" borderFillIDRef="1" textBorder="PAPER" headerInside="0" footerInside="0" fillArea="PAPER"><hp:offset left="1417" right="1417" top="1417" bottom="1417"/></hp:pageBorderFill><hp:pageBorderFill type="EVEN" borderFillIDRef="1" textBorder="PAPER" headerInside="0" footerInside="0" fillArea="PAPER"><hp:offset left="1417" right="1417" top="1417" bottom="1417"/></hp:pageBorderFill><hp:pageBorderFill type="ODD" borderFillIDRef="1" textBorder="PAPER" headerInside="0" footerInside="0" fillArea="PAPER"><hp:offset left="1417" right="1417" top="1417" bottom="1417"/></hp:pageBorderFill></hp:secPr><hp:ctrl><hp:colPr id="" type="NEWSPAPER" layout="LEFT" colCount="1" sameSz="1" sameGap="0"/></hp:ctrl></hp:run><hp:run charPrIDRef="0"><hp:pic id="2003360385" zOrder="0" numberingType="PICTURE" textWrap="SQUARE" textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" href="" groupLevel="0" instid="929618562" reverse="0"><hp:offset x="0" y="0"/><hp:orgSz width="{display_width}" height="{display_height}"/><hp:curSz width="0" height="0"/><hp:flip horizontal="0" vertical="0"/><hp:rotationInfo angle="0" centerX="{display_width//2}" centerY="{display_height//2}" rotateimage="1"/><hp:renderingInfo><hc:transMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/><hc:scaMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/><hc:rotMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/></hp:renderingInfo><hc:img binaryItemIDRef="image1" bright="0" contrast="0" effect="REAL_PIC" alpha="0"/><hp:imgRect><hc:pt0 x="0" y="0"/><hc:pt1 x="{img_width_hwp}" y="0"/><hc:pt2 x="{img_width_hwp}" y="{img_height_hwp}"/><hc:pt3 x="0" y="{img_height_hwp}"/></hp:imgRect><hp:imgClip left="0" right="{img_width_hwp}" top="0" bottom="{img_height_hwp}"/><hp:inMargin left="0" right="0" top="0" bottom="0"/><hp:imgDim dimwidth="{img_width_hwp}" dimheight="{img_height_hwp}"/><hp:effects/><hp:sz width="{display_width}" widthRelTo="ABSOLUTE" height="{display_height}" heightRelTo="ABSOLUTE" protect="0"/><hp:pos treatAsChar="0" affectLSpacing="0" flowWithText="1" allowOverlap="1" holdAnchorAndSO="0" vertRelTo="PAPER" horzRelTo="PAPER" vertAlign="TOP" horzAlign="LEFT" vertOffset="14351" horzOffset="10455"/><hp:outMargin left="0" right="0" top="0" bottom="0"/></hp:pic><hp:t/></hp:run><hp:linesegarray><hp:lineseg textpos="0" vertpos="0" vertsize="1000" textheight="1000" baseline="850" spacing="600" horzpos="0" horzsize="42520" flags="393216"/></hp:linesegarray></hp:p></hs:sec>'''

# section2.xml 제거하고 section0.xml만 사용
section2_path = os.path.join(temp_dir, "Contents", "section2.xml")
if os.path.exists(section2_path):
    # section2를 비우기
    with open(section2_path, 'r', encoding='utf-8') as f:
        orig = f.read()
    
    # 첫 <hp:p> 제거
    header_end = orig.find('<hp:p')
    footer_start = orig.rfind('</hs:sec>')
    
    empty_section = orig[:header_end] + '</hs:sec>'
    
    with open(section2_path, 'w', encoding='utf-8') as f:
        f.write(empty_section)

# section0.xml 생성
section0_path = os.path.join(temp_dir, "Contents", "section0.xml")
with open(section0_path, 'w', encoding='utf-8') as f:
    f.write(section_xml)

print("✓ section0.xml 생성 (PNG 이미지 포함)")

# 재압축
test_file = "hwp/PNG_CORRECT_FORMAT.hwpx"
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
print("📌 테스트 파일: hwp/PNG_CORRECT_FORMAT.hwpx")
print("="*80)
print("\n✅ PNG 원본 (소문자 .png)")
print("✅ imgClip/imgDim = 원본 이미지 크기")
print("✅ orgSz/curSz = 표시 크기")
print("✅ 비율 정확히 계산")
print("\n→ 이 파일 열어서 컬러 + 정상 크기 확인!")

