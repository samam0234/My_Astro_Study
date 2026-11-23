process.env.HOST = '127.0.0.1'; process.env.PORT = '4394';
process.env.SITE_URL = 'http://127.0.0.1:4394'; process.env.CORS_ORIGIN = process.env.SITE_URL;
process.env.DATABASE_URL = './data/e2e.sqlite'; process.env.DB_DRIVER = 'sqlite';
process.env.AI_MODE = 'mock'; process.env.INTEGRATIONS_MODE = 'mock';
await import('../dist/server/entry.mjs');
