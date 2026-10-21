import { useState } from 'react';

export default function MemoSearch({ memos = [] }) {
  const [query, setQuery] = useState('');
  const needle = query.trim().toLowerCase();
  const shown = memos.filter((memo) => {
    if (!needle) return true;
    return `${memo.title} ${memo.summary}`.toLowerCase().includes(needle);
  });

  return (
    <div className="search">
      <input
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        placeholder="제목, 요약 검색"
        aria-label="메모 검색"
      />
      {shown.length === 0 ? (
        <p>찾는 메모가 없습니다.</p>
      ) : (
        <ul className="memo-list">
          {shown.map((memo) => (
            <li key={memo.id}>
              <a href={`/memos/${memo.id}`}>{memo.title}</a>
              <p>
                {memo.minutes}분 · {memo.summary}
              </p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
