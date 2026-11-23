# study3 · 데이터 다루기

## ① 목표 한 줄

서버 변수와 브라우저 상태를 구분하고 로컬 메모를 저장한다.

기준: [Notion Astro](https://app.notion.com/p/3fdd7dec5e2e8136a3d7e7023440d36f). 실행 앱은 `course/` 하나다. 루트의 기존 study 문서를 이 과정으로 갱신했다.

## ② 📖 이론

서버의 `const items`는 HTML을 만들 때만 읽힌다. 브라우저에서 입력 중인 값은 `textarea.value`이며 이벤트 핸들러가 이를 저장한다. 이것이 이번 과정의 바인딩이다. 입력 → input 이벤트 → localStorage → 다음 방문 시 value 복구의 연결을 직접 작성한다.

서버 변수는 인쇄소의 원고, 브라우저 상태는 독자가 책에 붙인 메모에 가깝다. localStorage는 같은 출처·같은 브라우저에서만 유지된다. 로그인 비밀 토큰을 넣지 않으며, 여러 기기에서 공유할 데이터는 다음 DB API에 저장한다. 브라우저의 사생활 보호 설정이나 저장 용량 때문에 저장이 실패할 수 있어 try/catch가 필요하다.

## ③ 🛠️ 실기

`/lessons`에서 입력하고 새로고침한다. 입력 중 서버 요청은 발생하지 않는다. Network 탭에서 이를 확인한다. 문서 전체를 서버 파일로 저장하는 방법은 study6의 SQLite 파일 저장으로 확장한다. 이 단계의 데이터는 개인 초안이며 영구 DB의 원본이 아니다.

### `course/src/components/Draft.astro` 전체 코드

[Draft.astro](course/src/components/Draft.astro)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```astro
<label>로컬 메모 <textarea id="draft" placeholder="이 브라우저에만 저장합니다."></textarea></label>
<p id="draft-status" role="status"></p>
<script>
  const input = document.querySelector<HTMLTextAreaElement>('#draft')!;
  const status = document.querySelector('#draft-status')!;
  try { input.value = localStorage.getItem('astro-draft') || ''; }
  catch { status.textContent = '브라우저 저장소를 사용할 수 없습니다.'; }
  input.addEventListener('input', () => {
    try { localStorage.setItem('astro-draft', input.value); status.textContent = '이 브라우저에 저장했습니다.'; }
    catch { status.textContent = '저장 공간 또는 권한을 확인하세요.'; }
  });
</script>
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 2 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 3 | 브라우저에서 실행할 이벤트·DOM 코드의 경계를 정한다. |
| 4 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const input`. |
| 5 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const status`. |
| 6 | 이 브라우저에 이전에 저장한 초안을 읽어 입력값을 복구한다. |
| 7 | 실패 경로를 받아 사용자 오류 또는 내부 오류로 처리한다. |
| 8 | 브라우저 이벤트가 발생했을 때 실행할 함수를 연결한다. |
| 9 | 문자열을 HTML로 실행하지 않고 텍스트로 표시해 XSS 표면을 줄인다. |
| 10 | 실패 경로를 받아 사용자 오류 또는 내부 오류로 처리한다. |
| 11 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 12 | 브라우저에서 실행할 이벤트·DOM 코드의 경계를 정한다. |

## ④ 🔗 연동 포인트

`Draft.astro`의 `<script>`만 브라우저로 전달된다. localStorage 키 `astro-draft`는 서버에서 읽지 않는다. 다음 단계는 URL 쿼리에도 상태를 담아 공유 가능한 화면 주소를 만든다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| window is not defined | 서버에서 브라우저 API 사용 | script 안으로 이동 |
| 로컬 저장 실패 | 저장소 차단·용량 | 예외 처리와 사용자 안내 |

## ⑥ 직접 해보기

1. 메모를 작성하고 새로고침해 복구되는지 확인한다.
2. 개발자도구 Application에서 키를 지운 뒤 다시 연다.
3. 글자 수를 별도 `<output>`에 실시간 표시한다.

## ⑦ ☐ 체크리스트

- [ ] 서버 변수와 DOM 상태를 구분했다.
- [ ] input 이벤트로 화면과 저장소를 연결했다.
- [ ] 저장 실패 메시지와 복구 흐름을 만들었다.

## ⑧ 다음 단계 연결 문장

이 단계의 결과를 [study4.md](study4.md)에서 다음 기능과 연결한다. 학습자가 직접 확인할 체크는 의도적으로 비워 두며, 실제 실행 검증 결과는 [검증 기록](docs/verification.md)에 별도로 남긴다.
