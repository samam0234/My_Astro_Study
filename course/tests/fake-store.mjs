export function fakeStore() {
  const records = new Map(); let sequence = 0;
  return {
    async create(kind, value) { const row = structuredClone({ ...value, id: ++sequence }); records.set(`${kind}:${row.id}`, row); return structuredClone(row); },
    async list(kind) { return [...records.entries()].filter(([key]) => key.startsWith(`${kind}:`)).map(([, value]) => structuredClone(value)); },
    async get(kind, id) { return structuredClone(records.get(`${kind}:${id}`) || null); },
    async replace(kind, id, value) { records.set(`${kind}:${id}`, structuredClone({ ...value, id })); },
    async remove(kind, id) { records.delete(`${kind}:${id}`); },
    async close() {},
  };
}
