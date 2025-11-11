<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import type { Part } from './types';
	import { fly } from 'svelte/transition';

	export let part: Part;

	const dispatch = createEventDispatcher();

	let updatedPart = { ...part };

	async function savePart() {
		const res = await fetch(`/api/part/${updatedPart.id}`, {
			method: 'PUT',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(updatedPart)
		});

		if (res.ok) {
			dispatch('partSaved', updatedPart);
			close();
		} else {
			// Handle error
			console.error('Failed to save part');
		}
	}

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
		class="bg-gray-800 p-8 rounded-lg shadow-lg w-full max-w-2xl text-white"
		in:fly={{ y: -50, duration: 300 }}
		out:fly={{ y: -50, duration: 300 }}
	>
		<h2 class="text-3xl font-bold mb-6 border-b border-gray-700 pb-4">Edit Part</h2>

		<form on:submit|preventDefault={savePart}>
			<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
				<div class="flex flex-col">
					<label for="pn" class="font-semibold text-sm mb-2 text-gray-300">P/N</label>
					<input
						type="text"
						id="pn"
						bind:value={updatedPart.pn}
						class="w-full p-3 bg-gray-700 border border-gray-600 rounded-md"
					/>
				</div>
				<div class="flex flex-col">
					<label for="descriere" class="font-semibold text-sm mb-2 text-gray-300"
						>Descriere</label
					>
					<input
						type="text"
						id="descriere"
						bind:value={updatedPart.descriere}
						class="w-full p-3 bg-gray-700 border border-gray-600 rounded-md"
					/>
				</div>
			</div>

			<div class="flex justify-end gap-4 mt-8">
				<button
					type="button"
					on:click={close}
					class="bg-gray-600 text-gray-200 hover:bg-gray-500 font-semibold px-4 py-2 rounded-md"
					>Anuleaza</button
				>
				<button
					type="submit"
					class="bg-blue-600 text-white hover:bg-blue-700 font-semibold px-4 py-2 rounded-md"
					>Salveaza</button
				>
			</div>
		</form>
	</div>
</div>
