"""문서 구성·원문 체크·코드 동기화·파일 링크 검증."""
from pathlib import Path
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[1]
names=[f'study{i}.md' for i in range(11)]+['studyMidpoint.md']+[f'study{i}.md' for i in range(11,19)]+['studyFinal.md']
headers=['① 목표 한 줄','② 📖 이론','③ 🛠️ 실기','④ 🔗 연동 포인트','⑤ 오류 노트','⑥ 직접 해보기','⑦ ☐ 체크리스트','⑧ 다음 단계 연결 문장']
extras={
 'study6.md':'학습 목표의 예제 "정적 랜딩 + 게시판 목록 하나"를 스펙 v1 API(Express 또는 FastAPI)로 목록 읽기',
 'study10.md':'정적 빌드의 한계 기록: 글 작성 후 목록이 바뀌려면 재빌드 또는 <code>prerender = false</code>',
 'study11.md':'DB 칸이 정리 영역에 없다 → 저장소를 확인해 이 페이지에 기록 (DB 없음, 아래 저장 방식과 코드 스니펫)',
}
code_count=0
for name in names:
 p=ROOT/name; text=p.read_text(encoding='utf-8'); assert text.startswith('# study'),name
 positions=[text.index('## '+h) for h in headers]; assert positions==sorted(positions),name
 exercise=text.split('## ⑥ 직접 해보기',1)[1].split('## ⑦',1)[0]
 assert 2<=len(re.findall(r'^\d+\. ',exercise,re.M))<=3,name
 assert '- [ ] ' in text,name
 for match in re.finditer(r'^### `([^`]+)` 전체 코드\n.*?^```[^\n]*\n(.*?)\n```',text,re.M|re.S):
  path,code=match.groups(); assert (ROOT/path).read_text(encoding='utf-8').rstrip()==code,f'{name}: stale {path}'
  code_count+=1
 assert '줄별 설명:' in text,name
 if name in extras: assert '- [ ] '+extras[name] in text,name
 assert '\ufffd' not in text,name
 assert '???' not in text,name
for p in [*(ROOT/name for name in names),ROOT/'README.md',*(ROOT/'docs').glob('*.md')]:
 text=re.sub(r'```.*?```','',p.read_text(encoding='utf-8'),flags=re.S)
 for target in re.findall(r'\[[^\n]*?\]\(([^\s)]+)\)',text):
  if re.match(r'^(https?:|#|mailto:)',target):continue
  assert (p.parent/target.split('#')[0]).exists(),f'{p.name}: missing link {target}'
assert set(p.name for p in ROOT.glob('study*.md'))==set(names),'unexpected study file'
print(f'문서 {len(names)}개·8개 구성·전체 코드 {code_count}개·원문 체크 3개·로컬 링크 검증 통과')
