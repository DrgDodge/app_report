import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [
		tailwindcss(),
		sveltekit()
	],
	server: {
		hmr: false,
		proxy: {
			'/api': {
				target: 'http://backend:5000',
				changeOrigin: true
			}
		},
		allowedHosts: ['reportgen.lseb.top']
	}
});
