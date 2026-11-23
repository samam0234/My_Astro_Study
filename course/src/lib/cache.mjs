export function ttlCache(ttl = 2000, max = 100) {
  const entries = new Map();
  return {
    async get(key, load) {
      const cached = entries.get(key);
      if (cached && cached.expires > Date.now()) return structuredClone(cached.value);
      const value = await load();
      if (entries.size >= max) entries.delete(entries.keys().next().value);
      entries.set(key, { value: structuredClone(value), expires: Date.now() + ttl });
      return value;
    },
    clear() { entries.clear(); },
  };
}
export const postCache = ttlCache();
