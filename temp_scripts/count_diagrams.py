import sys, zipfile, re
sys.stdout.reconfigure(encoding='utf-8')

zf = zipfile.ZipFile('hwp/report_clean_tables_20251112_034443.hwpx', 'r')
xml = zf.read('Contents/section2.xml').decode('utf-8')
refs = re.findall(r'binaryItemIDRef="(diagram\d+)"', xml)

print(f'{len(refs)}개 diagram 참조:')
for r in refs:
    print(f'  {r}')

