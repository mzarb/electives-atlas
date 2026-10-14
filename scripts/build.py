"""Build the Electives Atlas from all elective PDFs in electives/."""
from pathlib import Path
import fitz, json, re, collections, sys
ROOT=Path(__file__).resolve().parents[1]
PDF_DIR=ROOT/'electives'
OUTPUT=ROOT/'dist'
EXCLUDED={'CE2020','CE2021','CE2022'}

ENGINEERING_COURSE_TITLES = {
    '0469': 'Mechanical Engineering',
    '0668': 'Renewable Energy Engineering',
    '0721': 'Robotics and Mechatronics',
    '0726': 'Engineering Design',
}


def parse_pdf(path):
    try:
        with fitz.open(path) as pdf:
            text='\n'.join(page.get_text() for page in pdf)
    except Exception as e:
        raise ValueError(f'{path.name}: could not read PDF: {e}') from e
    fm=re.match(r'Group\s+([A-Z]*\d+)\s*-\s*Electives\s*(\d+)\b',path.name,re.I)
    if not fm: raise ValueError(f'{path.name}: filename does not identify a course code and elective group')
    code, number=fm.groups()
    gt=re.search(r'Group Title\n(.+?)\nVersion',text,re.S)
    if not gt: raise ValueError(f'{path.name}: Group Title missing')
    title=gt.group(1).strip().removesuffix(' APPROVED')
    aff=text.split('Affiliated Entities')[-1]
    am=re.search(r'\n([A-Z]*\d+)\n(.+?)\n\d+\.\d+\nCourse',aff)
    # Some Akari group PDFs have no affiliated entity (the table says None).
    # In that case use the Group Title, just as the existing atlas does.
    affiliate=am.group(1) if am else None
    course=am.group(2).strip() if am else re.sub(r' - Electives? Group \d+$','',title)
    if code=='PS0531': course='BSc (Hons) Cyber Security'
    if code=='PS0679': course='BSc (Hons) Data Science Programme'
    if code in ENGINEERING_COURSE_TITLES:
        course = 'BEng / MEng ' + ENGINEERING_COURSE_TITLES[code]
    valid=re.search(r'Valid From\n(\d{4} [A-Za-z]+)',text)
    chunk=text.split('Group Deliveries')[-1].split('Affiliated Entities')[0]
    pat=re.compile(r'(?m)^([1-6])\nSemester\s*([123])\nElective\n([A-Z]{2,4}\d{3,4})\n([^\n]+)')
    matches=list(pat.finditer(chunk)); rows=[]
    if not matches: raise ValueError(f'{path.name}: no stage/semester/module rows recognised')
    for i,match in enumerate(matches):
        st,sem,mod,modtitle=match.groups()
        tail=chunk[match.end():matches[i+1].start() if i+1<len(matches) else len(chunk)]
        cm=re.search(r'\n(?:Yes|No)\n[\d.]+\n(\d+)\b',tail)
        if cm is None: raise ValueError(f'{path.name}: credit points not recognised for {mod}')
        if mod in EXCLUDED: continue
        rows.append(dict(stage=int(st),semester=int(sem),code=mod,title=modtitle.strip(),credits=int(cm.group(1))))
    return dict(courseCode=code,course=course,group=int(number),groupTitle=title,validFrom=valid.group(1) if valid else None,rows=rows,source=path.name,affiliated=True)

def main():
    paths=sorted(PDF_DIR.glob('*.pdf'))
    if not paths: raise ValueError('No PDFs found in electives/')
    groups=[parse_pdf(p) for p in paths]
    # Group numbering is not necessarily unique within a course (e.g. Group 1 and Group 1-2).
    # Retain distinct source PDFs, as the standalone Atlas did.
    names=collections.defaultdict(set)
    for g in groups: names[g['courseCode']].add(g['course'])
    mismatched={code:list(v) for code,v in names.items() if len(v)>1}
    if mismatched:raise ValueError(f'Inconsistent names for course code: {mismatched}')
    template=(ROOT/'web/template.html').read_text()
    output=template.replace('__ELECTIVES_DATA__',json.dumps(groups,ensure_ascii=False).replace('</','<\\/'))
    if output==template:raise ValueError('Missing data placeholder in template')
    output=re.sub(r'Source: .*?PDF documents[^<]*',f'Source: {len(groups)} elective-group PDFs in the repository. ',output)
    OUTPUT.mkdir(exist_ok=True)
    (OUTPUT/'index.html').write_text(output,encoding='utf-8')
    total=sum(len(g['rows']) for g in groups)
    print(f'Success: {len(names)} courses, {len(groups)} groups, {total} non-placement module entries')

if __name__=='__main__':
    try:main()
    except Exception as e:
        print(f'BUILD FAILED: {e}',file=sys.stderr)
        sys.exit(1)
