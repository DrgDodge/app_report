<script lang="ts">
	import { fly } from 'svelte/transition';
	import { createEventDispatcher } from 'svelte';
	import type { Client } from './types';

	export let clientDetails: { client: Client; utilaje: any[] };

	const dispatch = createEventDispatcher();

	function close() {
		dispatch('close');
	}
</script>

<div
	class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50"
	on:click|self={close}
	on:keydown|self={(e) => e.key === 'Escape' && close()}
	role="button"
	tabindex="0"
>
	<div
		class="bg-gray-800 p-8 rounded-lg shadow-lg w-full max-w-4xl text-white"
		in:fly={{ y: -50, duration: 300 }}
		out:fly={{ y: -50, duration: 300 }}
	>
		<button on:click={close} class="absolute top-4 right-4 text-gray-400 hover:text-white"
			>&times;</button
		>

		{#if clientDetails}
			<h2 class="text-3xl font-bold mb-6 border-b border-gray-700 pb-4">
				{clientDetails.client.nume}
			</h2>

			<div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
				<div>
					<h3 class="text-xl font-semibold mb-2 text-blue-400">Client Details</h3>
					<p><strong>CUI:</strong> {clientDetails.client.cui}</p>
					<p><strong>Adresa:</strong> {clientDetails.client.adresa}</p>
					<p><strong>Locatie:</strong> {clientDetails.client.locatie}</p>
				</div>
			</div>

			<div>
				<h3 class="text-xl font-semibold mb-4 text-blue-400">Utilaje</h3>
				<div class="space-y-4 max-h-96 overflow-y-auto">
					{#each clientDetails.utilaje as utilaj (utilaj.id)}
						<div class="bg-gray-700 p-4 rounded-lg">
							<p class="font-bold text-lg">{utilaj.nume}</p>
							<p class="text-gray-400">Serie: {utilaj.serie}</p>

							{#if utilaj.history && utilaj.history.length > 0}
								<div class="mt-3">
									<h5 class="text-md font-semibold mb-1 text-blue-300">
										Istoric Ore Functionare
									</h5>
									<ul class="list-disc list-inside text-gray-300">
										{#each utilaj.history as historyItem (historyItem.id)}
											<li>{historyItem.data}: {historyItem.ore_funct} ore</li>
										{/each}
									</ul>
								</div>
							{/if}
						</div>
					{/each}
				</div>
			</div>
		{/if}
	</div>
</div>
