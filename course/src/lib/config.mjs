export function settings(env = process.env) {
  return {
    site: env.SITE_URL || 'http://127.0.0.1:4323',
    driver: env.DB_DRIVER || 'sqlite',
    database: env.DATABASE_URL || './data/desk.sqlite',
    cors: env.CORS_ORIGIN || 'http://127.0.0.1:4323',
    production: env.NODE_ENV === 'production',
  };
}
