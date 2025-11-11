<script lang="ts">
	import { onMount } from 'svelte';
	import { createEventDispatcher } from 'svelte';
	import { fly } from 'svelte/transition';

	const dispatch = createEventDispatcher();

	interface RaportIstoric {
		id: number;
		numar_raport: string;
		client_nume_text: string;
		data: string;
	}

	let rapoarte: RaportIstoric[] = [];
	const API_BASE_URL = '/api';

	onMount(async () => {
		try {
			const res = await fetch(`${API_BASE_URL}/rapoarte`);
			if (res.ok) {
				rapoarte = await res.json();
			} else {
				console.error('Failed to fetch report history');
			}
		} catch (error) {
			console.error('Failed to fetch report history:', error);
		}
	});

	function editReport(id: number) {
		dispatch('edit', id);
	}

	function deleteReport(id: number) {
		dispatch('delete', id);
	}

	function generateReport(id: number) {
		dispatch('generate', id);
	}
</script>

<div
	class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50"
	on:click|self={() => dispatch('close')}
	on:keydown|self={(e) => e.key === 'Escape' && dispatch('close')}
	role="button"
	tabindex="0"
>
	<div
		class="bg-gray-800 rounded-lg shadow-xl p-6 w-full max-w-5xl max-h-[80vh] flex flex-col text-white"
		in:fly={{ y: -50, duration: 300 }}
		out:fly={{ y: -50, duration: 300 }}
	>
		<div class="flex justify-between items-center border-b border-gray-700 pb-3 mb-4">
			<h2 class="text-2xl font-bold">Istoric Rapoarte</h2>
			<button on:click={() => dispatch('close')} class="text-gray-400 hover:text-white text-2xl"
				>&times;</button
			>
		</div>
		<div class="overflow-y-auto">
			<table class="w-full border-collapse">
				<thead class="bg-gray-700 sticky top-0">
					<tr>
						<th class="border border-gray-600 p-3 text-left text-sm font-semibold"
							>Nr. Raport</th
						>
						<th class="border border-gray-600 p-3 text-left text-sm font-semibold">Client</th>
						<th class="border border-gray-600 p-3 text-left text-sm font-semibold">Data</th>
						<th class="border border-gray-600 p-3 text-left text-sm font-semibold">Actiuni</th>
					</tr>
				</thead>
				<tbody>
					{#each rapoarte as raport (raport.id)}
						<tr class="hover:bg-gray-700">
							<td class="border-t border-gray-700 p-3">{raport.numar_raport}</td>
							<td class="border-t border-gray-700 p-3">{raport.client_nume_text}</td>
							<td class="border-t border-gray-700 p-3">{raport.data}</td>
							<td class="border-t border-gray-700 p-3">
								<button
									on:click={() => editReport(raport.id)}
									class="bg-blue-600 text-white px-3 py-1 rounded-md text-sm hover:bg-blue-700"
									>Edit</button
								>
								<button
									on:click={() => deleteReport(raport.id)}
									class="bg-red-600 text-white px-3 py-1 rounded-md text-sm ml-2 hover:bg-red-700"
									>Delete</button
								>
								<button
									on:click={() => generateReport(raport.id)}
									class="bg-green-600 text-white px-3 py-1 rounded-md text-sm ml-2 hover:bg-green-700"
									>Generate</button
								>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</div>
</div>