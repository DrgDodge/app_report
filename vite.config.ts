import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import { SvelteKitPWA } from '@vite-pwa/sveltekit';

export default defineConfig({
	plugins: [
		tailwindcss(),
		SvelteKitPWA({
			manifest: {
				name: 'Raport Lucru',
				short_name: 'Raport',
				description: 'A work report generator application.',
				theme_color: '#ffffff',
				icons: [
					{
						src: 'logo.webp',
						sizes: '512x512',
						type: 'image/webp'
					},
					{
						src: 'favicon.svg',
						sizes: 'any',
						type: 'image/svg+xml'
					}
				]
			},
			devOptions: {
				enabled: true
			}
		}),
		sveltekit()
	],
	server: {
		proxy: {
			'/api': {
				target: 'http://backend:5000',
				changeOrigin: true
			}
		},
		allowedHosts: ['reportgen.lseb.top']
	}
});
