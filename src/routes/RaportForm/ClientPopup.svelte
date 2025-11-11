<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { fly } from 'svelte/transition';

	const dispatch = createEventDispatcher();

	let client = {
		nume: '',
		cui: '',
		nr_reg_com: '',
		iban: '',
		adresa: '',
		locatie: ''
	};

	async function saveClient() {
		const res = await fetch('/api/client', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(client)
		});

		if (res.ok) {
			const newClient = await res.json();
			dispatch('clientSaved', newClient);
			close();
		} else {
			// Handle error
			console.error('Failed to save client');
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
		<h2 class="text-3xl font-bold mb-6 border-b border-gray-700 pb-4">Adauga Client Nou</h2>

		<form on:submit|preventDefault={saveClient}>
			<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
				<div class="flex flex-col">
					<label for="nume" class="font-semibold text-sm mb-2 text-gray-300">Nume Firma</label>
					<input
						type="text"
						id="nume"
						bind:value={client.nume}
						class="w-full p-3 bg-gray-700 border border-gray-600 rounded-md"
					/>
				</div>
				<div class="flex flex-col">
					<label for="cui" class="font-semibold text-sm mb-2 text-gray-300">CUI</label>
					<input
						type="text"
						id="cui"
						bind:value={client.cui}
						class="w-full p-3 bg-gray-700 border border-gray-600 rounded-md"
					/>
				</div>
				<div class="flex flex-col">
					<label for="nr_reg_com" class="font-semibold text-sm mb-2 text-gray-300"
						>Nr. Reg. Com.</label
					>
					<input
						type="text"
						id="nr_reg_com"
						bind:value={client.nr_reg_com}
						class="w-full p-3 bg-gray-700 border border-gray-600 rounded-md"
					/>
				</div>
				<div class="flex flex-col">
					<label for="iban" class="font-semibold text-sm mb-2 text-gray-300">IBAN</label>
					<input
						type="text"
						id="iban"
						bind:value={client.iban}
						class="w-full p-3 bg-gray-700 border border-gray-600 rounded-md"
					/>
				</div>
				<div class="flex flex-col col-span-2">
					<label for="adresa" class="font-semibold text-sm mb-2 text-gray-300">Adresa</label>
					<input
						type="text"
						id="adresa"
						bind:value={client.adresa}
						class="w-full p-3 bg-gray-700 border border-gray-600 rounded-md"
					/>
				</div>
				<div class="flex flex-col col-span-2">
					<label for="locatie" class="font-semibold text-sm mb-2 text-gray-300">Locatie</label>
					<input
						type="text"
						id="locatie"
						bind:value={client.locatie}
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
					>Salveaza Client</button
				>
			</div>
		</form>
	</div>
</div>