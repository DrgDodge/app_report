<script lang="ts">
	import '../app.css';
	import { fade } from 'svelte/transition';
	import { Github } from 'lucide-svelte';
</script>

<svelte:head>
	<meta name="theme-color" content="#1a202c" />
	<link
		rel="manifest"
		href="data:application/manifest+json;base64,ewogICJuYW1lIjogIlJhcG9ydCBMdWNydSIsCiAgInNob3J0X25hbWUiOiAiUmFwb3J0IiwKICAiZGVzY3JpcHRpb24iOiAiQSB3b3JrIHJlcG9ydCBnZW5lcmF0b3IgYXBwbGljYXRpb24uIiwKICAic3RhcnRfdXJsIjogImh0dHBzOi8vcmVwb3J0Z2VuLmxzZWIudG9wLyIsCiAgImRpc3BsYXkiOiAic3RhbmRhbG9uZSIsCiAgImJhY2tncm91bmRfY29sb3IiOiAiI2ZmZmZmZiIsCiAgInRoZW1lX2NvbG9yIjogIiNmZmZmZmYiLAogICJpY29ucyI6IFsKICAgIHsKICAgICAgInNyYyI6ICJodHRwczovL3JlcG9ydGdlbi5sc2ViLnRvcC9sb2dvLndlYnAiLAogICAgICAic2l6ZXMiOiAiNTEyeDUxMiIsCiAgICAgICJ0eXBlIjogImltYWdlL3dlYnAiCiAgICB9LAogICAgewoKICAgICAgInNyYyI6ICJodHRwczovL3JlcG9ydGdlbi5sc2ViLnRvcC9mYXZpY29uLnN2ZyIsCiAgICAgICJzaXplcyI6ICJhbnkiLAogICAgICAidHlwZSI6ICJpbWFnZS9zdmcreG1sIgogICAgfQogIF0KfQo="
	/>
</svelte:head>

<div class="min-h-screen flex flex-col bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-gray-200">
	<header class="bg-white dark:bg-gray-800 shadow-md sticky top-0 z-50">
		<nav class="max-w-7xl mx-auto px-4 py-3">
			<div class="flex justify-between items-center">
				<a href="/" class="text-2xl font-bold text-gray-900 dark:text-white">Generator Rapoarte</a>
				<div class="hidden md:flex items-center gap-6">
					<a
						href="/RaportForm"
						class="text-lg font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
						>Raport Form</a
					>
					<a
						href="/database"
						class="text-lg font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
						>Database</a
					>
					<a
						href="/admin"
						class="text-lg font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
						>Admin</a
					>
				</div>
				<div class="flex items-center gap-4">
					<a
						href="https://github.com/your-repo"
						target="_blank"
						rel="noopener noreferrer"
						class="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
					>
						<Github class="w-6 h-6" />
					</a>
				</div>
			</div>
		</nav>
	</header>

	<main class="flex-grow container mx-auto p-4 sm:p-6 lg:p-8" in:fade={{ duration: 300 }}>
		<slot />
	</main>

	<footer class="bg-white dark:bg-gray-800 text-center p-4 mt-auto">
		&copy; {new Date().getFullYear()} Toate drepturile rezervate.
	</footer>
</div>
