// @ts-check
import { defineConfig } from 'astro/config';
import { fileURLToPath } from 'node:url';
import react from '@astrojs/react';
import vue from '@astrojs/vue';
import svelte from '@astrojs/svelte';

const repoRoot = fileURLToPath(new URL('..', import.meta.url));
const demoPackage = fileURLToPath(new URL('./package.json', import.meta.url));

/** 섬 파일은 demo 밖에 있어서, 그 위치에서는 demo/node_modules를 못 찾는다. */
function islandResolve() {
  return {
    name: 'island-resolve',
    enforce: 'pre',
    async resolveId(id, importer, options) {
      if (!importer || id.startsWith('.') || id.startsWith('\0') || id.startsWith('island-')) return null;
      const fromIsland = /[/\\](react|vue|svelte)[/\\]demo[/\\]/.test(importer);
      if (!fromIsland) return null;
      return this.resolve(id, demoPackage, { ...options, skipSelf: true });
    },
  };
}

// https://astro.build/config
export default defineConfig({
  site: 'http://127.0.0.1:4321',
  server: {
    host: '127.0.0.1',
    port: 4321,
  },
  integrations: [react(), vue(), svelte()],
  vite: {
    plugins: [islandResolve()],
    resolve: {
      alias: {
        'island-react': fileURLToPath(new URL('../react/demo', import.meta.url)),
        'island-vue': fileURLToPath(new URL('../vue/demo', import.meta.url)),
        'island-svelte': fileURLToPath(new URL('../svelte/demo', import.meta.url)),
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
