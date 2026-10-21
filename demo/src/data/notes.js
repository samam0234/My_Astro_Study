/** study2에서 경로를 확인하기 위한 임시 목록. study5에서 콘텐츠 컬렉션으로 바꿉니다. */
export const notes = [
  {
    slug: 'static-html',
    title: '정적 HTML',
    summary: '빌드가 HTML 파일을 만들고, 브라우저 JavaScript는 없습니다.',
  },
  {
    slug: 'file-is-url',
    title: '파일이 주소다',
    summary: 'src/pages 아래 경로가 곧 URL입니다.',
  },
];

export function findNote(slug) {
  return notes.find((note) => note.slug === slug);
}
