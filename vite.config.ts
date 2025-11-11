import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
	plugins: [
		sveltekit(),
		tailwindcss()
	],
	server: {
		hmr: false,
		proxy: {
			'/api': {
				target: 'http://backend:5000',
				changeOrigin: true
			}
		}
	}
});
