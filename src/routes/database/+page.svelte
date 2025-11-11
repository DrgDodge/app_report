<script lang="ts">
	import { onMount } from 'svelte';
	import { fade } from 'svelte/transition';
	import ClientDetailsPopup from './ClientDetailsPopup.svelte';
	import EditPartPopup from './EditPartPopup.svelte';
	import EditClientPopup from './EditClientPopup.svelte';
	import type { Client, Part } from './types';

	let clients = $state<Client[]>([]);
	let parts = $state<Part[]>([]);
	let selectedClientDetails = $state<{ client: Client; utilaje: any[] } | null>(null);
	let clientSearch = $state('');
	let partSearch = $state('');
	let editingPart = $state<Part | null>(null);
	let editingClient = $state<Client | null>(null);
	let activeTab = $state<'clients' | 'parts'>('clients');

	onMount(async () => {
		const resClients = await fetch('/api/clients');
		clients = await resClients.json();

		const resParts = await fetch('/api/parts');
		parts = await resParts.json();
	});

	async function showClientDetails(clientId: number) {
		const res = await fetch(`/api/client/${clientId}/full_details`);
		selectedClientDetails = await res.json();
	}

	function handlePartSaved(event: CustomEvent<Part>) {
		const updatedPart = event.detail;
		const index = parts.findIndex((p) => p.id === updatedPart.id);
		if (index !== -1) {
			parts[index] = updatedPart;
		}
		editingPart = null;
	}

	function handleClientSaved(event: CustomEvent<Client>) {
		const updatedClient = event.detail;
		const index = clients.findIndex((c) => c.id === updatedClient.id);
		if (index !== -1) {
			clients[index] = updatedClient;
		}
		editingClient = null;
	}

	async function deleteClient(clientId: number) {
		if (confirm('Are you sure you want to delete this client?')) {
			const res = await fetch(`/api/client/${clientId}`, { method: 'DELETE' });
			if (res.ok) {
				clients = clients.filter((c) => c.id !== clientId);
			} else {
				const data = await res.json();
				alert(data.message);
			}
		}
	}

	async function deletePart(partId: number) {
		if (confirm('Are you sure you want to delete this part?')) {
			const res = await fetch(`/api/part/${partId}`, { method: 'DELETE' });
			if (res.ok) {
				parts = parts.filter((p) => p.id !== partId);
			} else {
				const data = await res.json();
				alert(data.message);
			}
		}
	}

	$: filteredClients = clients.filter((client) =>
		client.nume.toLowerCase().includes(clientSearch.toLowerCase())
	);
	$: filteredParts = parts.filter(
		(part) =>
			part.pn.toLowerCase().includes(partSearch.toLowerCase()) ||
			part.descriere.toLowerCase().includes(partSearch.toLowerCase())
	);
</script>

<div class="container mx-auto p-8 bg-gray-800 rounded-lg shadow-lg">
	<div class="flex border-b border-gray-700">
		<button
			class="py-2 px-4 text-lg font-semibold transition-colors"
			class:text-blue-400={activeTab === 'clients'}
			class:border-b-2={activeTab === 'clients'}
			class:border-blue-400={activeTab === 'clients'}
			class:text-gray-400={activeTab !== 'clients'}
			on:click={() => (activeTab = 'clients')}
		>
			Clients
		</button>
		<button
			class="py-2 px-4 text-lg font-semibold transition-colors"
			class:text-blue-400={activeTab === 'parts'}
			class:border-b-2={activeTab === 'parts'}
			class:border-blue-400={activeTab === 'parts'}
			class:text-gray-400={activeTab !== 'parts'}
			on:click={() => (activeTab = 'parts')}
		>
			Parts
		</button>
	</div>

	<div class="mt-8">
		{#if activeTab === 'clients'}
			<div in:fade>
				<h2 class="text-2xl font-bold mb-4 text-white">Clients</h2>
				<input
					type="text"
					placeholder="Search Clients..."
					class="w-full p-3 bg-gray-700 border border-gray-600 rounded-md mb-4 text-white"
					bind:value={clientSearch}
				/>
				<ul class="space-y-2">
					{#each filteredClients as client (client.id)}
						<li
							class="p-4 bg-gray-700 rounded-md flex justify-between items-center transition-transform hover:scale-105"
						>
							<button
								class="w-full text-left text-white"
								on:click={() => showClientDetails(client.id)}
							>
								{client.nume}
							</button>
							<div>
								<button
									class="bg-blue-600 text-white px-3 py-1 rounded-md hover:bg-blue-700"
									on:click={() => (editingClient = client)}>Edit</button
								>
								<button
									class="bg-red-600 text-white px-3 py-1 rounded-md ml-2 hover:bg-red-700"
									on:click={() => deleteClient(client.id)}>Delete</button
								>
							</div>
						</li>
					{/each}
				</ul>
			</div>
		{/if}

		{#if activeTab === 'parts'}
			<div in:fade>
				<h2 class="text-2xl font-bold mb-4 text-white">Parts</h2>
				<input
					type="text"
					placeholder="Search Parts..."
					class="w-full p-3 bg-gray-700 border border-gray-600 rounded-md mb-4 text-white"
					bind:value={partSearch}
				/>
				<ul class="space-y-2">
					{#each filteredParts as part (part.id)}
						<li
							class="p-4 bg-gray-700 rounded-md flex justify-between items-center transition-transform hover:scale-105"
						>
							<span class="text-white">{part.pn} - {part.descriere}</span>
							<div>
								<button
									class="bg-blue-600 text-white px-3 py-1 rounded-md hover:bg-blue-700"
									on:click={() => (editingPart = part)}>Edit</button
								>
								<button
									class="bg-red-600 text-white px-3 py-1 rounded-md ml-2 hover:bg-red-700"
									on:click={() => deletePart(part.id)}>Delete</button
								>
							</div>
						</li>
					{/each}
				</ul>
			</div>
		{/if}
	</div>
</div>

{#if selectedClientDetails}
	<ClientDetailsPopup
		clientDetails={selectedClientDetails}
		on:close={() => (selectedClientDetails = null)}
	/>
{/if}

{#if editingPart}
	<EditPartPopup {editingPart} on:close={() => (editingPart = null)} on:partSaved={handlePartSaved} />
{/if}

{#if editingClient}
	<EditClientPopup
		{editingClient}
		on:close={() => (editingClient = null)}
		on:clientSaved={handleClientSaved}
	/>
{/if}
