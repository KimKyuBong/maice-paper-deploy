"""
content.hpf에 이미지 등록 추가
"""
import sys
import zipfile
import shutil
import os
import hashlib
import base64

sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("content.hpf 업데이트 테스트")
print("="*80)

# 원본 복사
original = "hwp/report_backup_20251112_020239.hwpx"
temp_dir = "hwp/temp_hpf_fix"

if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)

with zipfile.ZipFile(original, 'r') as zf:
    zf.extractall(temp_dir)

# BinData 비우기
bindata_dir = os.path.join(temp_dir, "BinData")
for f in os.listdir(bindata_dir):
    os.remove(os.path.join(bindata_dir, f))

# PNG 복사
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

# content.hpf 읽기
hpf_path = os.path.join(temp_dir, "Contents", "content.hpf")
with open(hpf_path, 'r', encoding='utf-8') as f:
    hpf_content = f.read()

print(f"\n원본 content.hpf 크기: {len(hpf_content)} bytes")

# manifest에서 기존 이미지 항목 모두 제거
import re

# <opf:item id="imageN" ... /> 패턴 모두 제거
hpf_content = re.sub(r'<opf:item id="image\d+"[^>]*/>', '', hpf_content)

# 새 이미지 항목 추가
new_item = f'<opf:item id="image1" href="BinData/image1.png" media-type="image/png" isEmbeded="1" hashkey="{hashkey}"/>'

# </opf:manifest> 앞에 삽입
manifest_end = hpf_content.find('</opf:manifest>')
if manifest_end != -1:
    hpf_content = hpf_content[:manifest_end] + new_item + hpf_content[manifest_end:]
    print(f"✓ content.hpf에 image1 등록")
else:
    print("✗ manifest 태그 없음!")

# 저장
with open(hpf_path, 'w', encoding='utf-8') as f:
    f.write(hpf_content)

print(f"✓ content.hpf 업데이트 완료")

# section0.xml 생성 (간단한 테스트)
from PIL import Image

img = Image.open(png_file)
width_px, height_px = img.size
dpi = img.info.get('dpi', (96, 96))[0]

img_width_hwp = int(width_px / dpi * 7200)
img_height_hwp = int(height_px / dpi * 7200)

max_width = 80000
if img_width_hwp > max_width:
    scale = max_width / img_width_hwp
    display_width = max_width
    display_height = int(img_height_hwp * scale)
else:
    display_width = img_width_hwp
    display_height = img_height_hwp

section_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes" ?><hs:sec xmlns:ha="http://www.hancom.co.kr/hwpml/2011/app" xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph" xmlns:hp10="http://www.hancom.co.kr/hwpml/2016/paragraph" xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section" xmlns:hc="http://www.hancom.co.kr/hwpml/2011/core" xmlns:hh="http://www.hancom.co.kr/hwpml/2011/head" xmlns:hhs="http://www.hancom.co.kr/hwpml/2011/history" xmlns:hm="http://www.hancom.co.kr/hwpml/2011/master-page" xmlns:hpf="http://www.hancom.co.kr/schema/2011/hpf" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf/" xmlns:ooxmlchart="http://www.hancom.co.kr/hwpml/2016/ooxmlchart" xmlns:hwpunitchar="http://www.hancom.co.kr/hwpml/2016/HwpUnitChar" xmlns:epub="http://www.idpf.org/2007/ops" xmlns:config="urn:oasis:names:tc:opendocument:xmlns:config:1.0"><hp:p id="3121190098" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="0"><hp:secPr id="" textDirection="HORIZONTAL" spaceColumns="1134" tabStop="8000" tabStopVal="4000" tabStopUnit="HWPUNIT" outlineShapeIDRef="1" memoShapeIDRef="1" textVerticalWidthHead="0" masterPageCnt="0"><hp:grid lineGrid="0" charGrid="0" wonggojiFormat="0"/><hp:startNum pageStartsOn="BOTH" page="0" pic="0" tbl="0" equation="0"/><hp:visibility hideFirstHeader="0" hideFirstFooter="0" hideFirstMasterPage="0" border="SHOW_ALL" fill="SHOW_ALL" hideFirstPageNum="0" hideFirstEmptyLine="0" showLineNumber="0" lineNumberShape restartType="0" countBy="0" distance="0" startNumber="0"/><hp:lineNumberShape restartType="0" countBy="0" distance="0" startNumber="0"/><hp:pagePr landscape="WIDELY" width="59528" height="84186" gutterType="LEFT_ONLY"><hp:margin header="4252" footer="4252" gutter="0" left="8504" right="8504" top="5668" bottom="4252"/></hp:pagePr><hp:footNotePr><hp:autoNumFormat type="DIGIT" userChar="" prefixChar="" suffixChar=")" supscript="0"/><hp:noteLine length="-1" type="SOLID" width="0.12 mm" color="#000000"/><hp:noteSpacing betweenNotes="283" belowLine="567" aboveLine="850"/><hp:numbering type="CONTINUOUS" newNum="1"/><hp:placement place="EACH_COLUMN" beneathText="0"/></hp:footNotePr><hp:endNotePr><hp:autoNumFormat type="DIGIT" userChar="" prefixChar="" suffixChar=")" supscript="0"/><hp:noteLine length="14692344" type="SOLID" width="0.12 mm" color="#000000"/><hp:noteSpacing betweenNotes="0" belowLine="567" aboveLine="850"/><hp:numbering type="CONTINUOUS" newNum="1"/><hp:placement place="END_OF_DOCUMENT" beneathText="0"/></hp:endNotePr><hp:pageBorderFill type="BOTH" borderFillIDRef="1" textBorder="PAPER" headerInside="0" footerInside="0" fillArea="PAPER"><hp:offset left="1417" right="1417" top="1417" bottom="1417"/></hp:pageBorderFill><hp:pageBorderFill type="EVEN" borderFillIDRef="1" textBorder="PAPER" headerInside="0" footerInside="0" fillArea="PAPER"><hp:offset left="1417" right="1417" top="1417" bottom="1417"/></hp:pageBorderFill><hp:pageBorderFill type="ODD" borderFillIDRef="1" textBorder="PAPER" headerInside="0" footerInside="0" fillArea="PAPER"><hp:offset left="1417" right="1417" top="1417" bottom="1417"/></hp:pageBorderFill></hp:secPr><hp:ctrl><hp:colPr id="" type="NEWSPAPER" layout="LEFT" colCount="1" sameSz="1" sameGap="0"/></hp:ctrl></hp:run><hp:run charPrIDRef="0"><hp:pic id="2003360385" zOrder="0" numberingType="PICTURE" textWrap="SQUARE" textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" href="" groupLevel="0" instid="929618562" reverse="0"><hp:offset x="0" y="0"/><hp:orgSz width="30763" height="19224"/><hp:curSz width="0" height="0"/><hp:flip horizontal="0" vertical="0"/><hp:rotationInfo angle="0" centerX="15381" centerY="9612" rotateimage="1"/><hp:renderingInfo><hc:transMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/><hc:scaMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/><hc:rotMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/></hp:renderingInfo><hc:img binaryItemIDRef="image1" bright="0" contrast="0" effect="REAL_PIC" alpha="0"/><hp:imgRect><hc:pt0 x="0" y="0"/><hc:pt1 x="30763" y="0"/><hc:pt2 x="30763" y="19224"/><hc:pt3 x="0" y="19224"/></hp:imgRect><hp:imgClip left="0" right="96000" top="0" bottom="60000"/><hp:inMargin left="0" right="0" top="0" bottom="0"/><hp:imgDim dimwidth="96000" dimheight="60000"/><hp:effects/><hp:sz width="30763" widthRelTo="ABSOLUTE" height="19224" heightRelTo="ABSOLUTE" protect="0"/><hp:pos treatAsChar="0" affectLSpacing="0" flowWithText="1" allowOverlap="1" holdAnchorAndSO="0" vertRelTo="PAPER" horzRelTo="PAPER" vertAlign="TOP" horzAlign="LEFT" vertOffset="14351" horzOffset="10455"/><hp:outMargin left="0" right="0" top="0" bottom="0"/><hp:shapeComment>그림입니다.
원본 그림의 이름: 다운로드.png
원본 그림의 크기: 가로 1280pixel, 세로 800pixel</hp:shapeComment></hp:pic><hp:t/></hp:run><hp:linesegarray><hp:lineseg textpos="0" vertpos="0" vertsize="1000" textheight="1000" baseline="850" spacing="600" horzpos="0" horzsize="42520" flags="393216"/></hp:linesegarray></hp:p></hs:sec>

```

Command completed.

The previous shell command ended, so on the next invocation of this tool, you will be reusing the shell.</output>
</result>
