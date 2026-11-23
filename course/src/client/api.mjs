import { formSchemas } from './schemas.mjs';
export function show(value) {
  const target = document.querySelector('#message');
  if (target) target.textContent = value instanceof Error ? value.message : String(value);
}
export async function api(path, options = {}) {
  const response = await fetch(path, { credentials: 'same-origin', ...options,
    headers: { 'Content-Type': 'application/json', ...options.headers } });
  if (response.status === 204) return null;
  const result = await response.json();
  if (!response.ok) {
    const fields = result.error?.fields || {};
    const detail = Object.entries(fields).map(([name, errors]) => `${name}: ${errors.join(', ')}`).join(' / ');
    const message = [200, 201].includes(response.status) ? '완료' : response.status === 422 ? '입력 형식을 확인하세요.' : result.error?.message || '요청 실패';
    throw new Error(`${response.status} ${message}${detail ? ` (${detail})` : ''}`);
  }
  return result;
}
export function formAction(selector, action) {
  const form = document.querySelector(selector);
  let busy = false;
  form.addEventListener('submit', async event => {
    event.preventDefault(); if (busy || !form.reportValidity()) return;
    busy = true; const buttons = [...form.querySelectorAll('button:not([type=button])')]; buttons.forEach(b => b.disabled = true);
    try {
      const values = Object.fromEntries(new FormData(form)), schema = formSchemas[selector];
      const checked = schema?.safeParse(values);
      if (checked && !checked.success) throw new Error(checked.error.issues.map(issue => `${issue.path.join('.')}: ${issue.message}`).join(' / '));
      await action(checked ? checked.data : values);
    }
    catch (error) { show(error); }
    finally { busy = false; buttons.forEach(b => b.disabled = false); }
  });
}
