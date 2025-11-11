<script lang="ts">
	import { sineIn } from 'svelte/easing';
	import { writable } from 'svelte/store';
	import { fade, slide } from 'svelte/transition';
	import '../app.css';

	let isOpen = writable(false);

	function toggleMenu() {
		isOpen.update((value) => !value);
	}
</script>

<div class="min-h-screen bg-gray-900 text-white flex">
	<!-- Sidebar -->
	<aside
		class="w-64 bg-gray-800 shadow-md flex-shrink-0 transition-all duration-300 ease-in-out"
		class:w-20={$isOpen}
	>
		<div class="p-5 flex items-center" class:justify-center={$isOpen}>
			<a href="/" class="text-2xl font-bold">
				{#if !$isOpen}
					<span in:fade={{ duration: 300, delay: 300 }}>Generator Rapoarte</span>
				{:else}
					<span in:fade={{ duration: 300, delay: 300 }}>GR</span>
				{/if}
			</a>
		</div>
		<nav class="mt-10">
			<a
				href="/RaportForm"
				class="flex items-center py-3 px-5 text-lg hover:bg-gray-700 transition-colors"
				class:justify-center={$isOpen}
			>
				<svg
					class="h-6 w-6"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
					></path>
				</svg>
				{#if !$isOpen}
					<span class="ml-4" in:fade={{ duration: 300, delay: 300 }}>Raport Form</span>
				{/if}
			</a>
			<a
				href="/database"
				class="flex items-center py-3 px-5 text-lg hover:bg-gray-700 transition-colors"
				class:justify-center={$isOpen}
			>
				<svg
					class="h-6 w-6"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M4 7v10m16-10v10M4 13h16M4 7a2 2 0 012-2h12a2 2 0 012 2m-2 10a2 2 0 002-2V7a2 2 0 00-2-2H6a2 2 0 00-2 2v10a2 2 0 002 2z"
					></path>
				</svg>
				{#if !$isOpen}
					<span class="ml-4" in:fade={{ duration: 300, delay: 300 }}>Database</span>
				{/if}
			</a>
			<a
				href="/admin"
				class="flex items-center py-3 px-5 text-lg hover:bg-gray-700 transition-colors"
				class:justify-center={$isOpen}
			>
				<svg
					class="h-6 w-6"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
					></path>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
					></path>
				</svg>
				{#if !$isOpen}
					<span class="ml-4" in:fade={{ duration: 300, delay: 300 }}>Admin</span>
				{/if}
			</a>
		</nav>
	</aside>

	<!-- Main Content -->
	<div class="flex-1 flex flex-col overflow-hidden">
		<header class="bg-gray-800 shadow-md p-4 flex justify-between items-center">
			<button on:click={toggleMenu} class="text-white focus:outline-none">
				<svg
					class="h-6 w-6"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M4 6h16M4 12h16M4 18h16"
					></path>
				</svg>
			</button>
			<h1 class="text-xl font-semibold">Dashboard</h1>
		</header>
		<main
			class="flex-1 overflow-x-hidden overflow-y-auto bg-gray-900 p-6"
			in:slide={{ duration: 500, easing: sineIn }}
		>
			<slot />
		</main>
	</div>
</div>