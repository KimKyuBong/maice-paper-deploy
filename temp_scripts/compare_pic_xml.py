"""
원본 vs 생성된 이미지 XML 정확 비교
"""
import sys
import zipfile

sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("원본 vs 생성된 이미지 XML 비교")
print("="*80)

# 원본
original = "hwp/report_backup_20251112_020239.hwpx"
with zipfile.ZipFile(original, 'r') as zf:
    xml = zf.read('Contents/section2.xml').decode('utf-8')
    
    pic_start = xml.find('<hp:pic ')
    p_start = xml.rfind('<hp:p ', 0, pic_start)
    p_end = xml.find('</hp:p>', pic_start) + len('</hp:p>')
    
    original_para = xml[p_start:p_end]

# 생성된 파일
generated = "hwp/report_with_images_20251112_033511.hwpx"
with zipfile.ZipFile(generated, 'r') as zf:
    xml = zf.read('Contents/section2.xml').decode('utf-8')
    
    pic_start = xml.find('<hp:pic ')
    p_start = xml.rfind('<hp:p ', 0, pic_start)
    p_end = xml.find('</hp:p>', pic_start) + len('</hp:p>')
    
    generated_para = xml[p_start:p_end]

# 비교
print("\n원본 이미지 문단:")
print("-"*80)
print(original_para)

print("\n\n생성된 이미지 문단:")
print("-"*80)
print(generated_para)

# 차이점 찾기
print("\n\n" + "="*80)
print("차이점:")
print("="*80)

import difflib
diff = difflib.unified_diff(
    original_para.splitlines(keepends=True),
    generated_para.splitlines(keepends=True),
    lineterm='',
    fromfile='원본',
    tofile='생성'
)

print(''.join(diff))

