// @ts-check
import { defineConfig } from 'astro/config';
import { fileURLToPath } from 'node:url';
import node from '@astrojs/node';
import mdx from '@astrojs/mdx';
import react from '@astrojs/react';
import vue from '@astrojs/vue';
import svelte from '@astrojs/svelte';

const repoRoot = fileURLToPath(new URL('..', import.meta.url));
const projectPackage = fileURLToPath(new URL('./package.json', import.meta.url));

function islandResolve() {
  return {
    name: 'island-resolve',
    enforce: 'pre',
    async resolveId(id, importer, options) {
      if (!importer || id.startsWith('.') || id.startsWith('\0') || id.startsWith('island-')) return null;
      const fromIsland = /[/\\](react|vue|svelte)[/\\]project[/\\]/.test(importer);
      if (!fromIsland) return null;
      return this.resolve(id, projectPackage, { ...options, skipSelf: true });
    },
  };
}

export default defineConfig({
  site: 'http://127.0.0.1:4322',
  server: {
    host: '127.0.0.1',
    port: 4322,
  },
  adapter: node({ mode: 'standalone' }),
  integrations: [mdx(), react(), vue(), svelte()],
  vite: {
    plugins: [islandResolve()],
    resolve: {
      alias: {
        'island-react': fileURLToPath(new URL('../react/project', import.meta.url)),
        'island-vue': fileURLToPath(new URL('../vue/project', import.meta.url)),
        'island-svelte': fileURLToPath(new URL('../svelte/project', import.meta.url)),
      },
      dedupe: ['react', 'react-dom', 'vue', 'svelte'],
    },
    server: {
      fs: {
        allow: [repoRoot],
      },
    },
  },
});
