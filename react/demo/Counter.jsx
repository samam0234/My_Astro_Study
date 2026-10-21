import { useState } from 'react';

export default function Counter({ label = 'React' }) {
  const [count, setCount] = useState(0);

  return (
    <button className="island-button" type="button" onClick={() => setCount((value) => value + 1)}>
      {label} {count}
    </button>
  );
}
