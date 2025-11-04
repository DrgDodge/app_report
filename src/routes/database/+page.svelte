<script lang="ts">
    import { onMount } from 'svelte';
    import ClientDetailsPopup from './ClientDetailsPopup.svelte';
    import EditPartPopup from './EditPartPopup.svelte';
    import EditClientPopup from './EditClientPopup.svelte';
    import type { Client, Part } from './types';

    let clients: Client[] = [];
    let parts: Part[] = [];
    let selectedClientDetails: { client: Client, utilaje: any[] } | null = null;
    let clientSearch = '';
    let partSearch = '';
    let editingPart: Part | null = null;
    let editingClient: Client | null = null;

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

    function editPart(part: Part) {
        editingPart = part;
    }

    function editClient(client: Client) {
        editingClient = client;
    }

    function handlePartSaved(event: CustomEvent<Part>) {
        const updatedPart = event.detail;
        const index = parts.findIndex(p => p.id === updatedPart.id);
        if (index !== -1) {
            parts[index] = updatedPart;
        }
        editingPart = null;
    }

    function handleClientSaved(event: CustomEvent<Client>) {
        const updatedClient = event.detail;
        const index = clients.findIndex(c => c.id === updatedClient.id);
        if (index !== -1) {
            clients[index] = updatedClient;
        }
        editingClient = null;
    }

    $: filteredClients = clients.filter(client => client.nume.toLowerCase().includes(clientSearch.toLowerCase()));
    $: filteredParts = parts.filter(part => part.pn.toLowerCase().includes(partSearch.toLowerCase()) || part.descriere.toLowerCase().includes(partSearch.toLowerCase()));
</script>

<div class="grid grid-cols-2 gap-8">
    <div>
        <h2 class="text-2xl font-bold mb-4">Clients</h2>
        <input type="text" placeholder="Search Clients..." class="w-full p-2 border border-gray-300 rounded-md mb-2" bind:value={clientSearch} />
        <ul class="divide-y divide-gray-200">
            {#each filteredClients as client (client.id)}
                <li class="py-2 flex justify-between items-center">
                    <button class="w-full text-left py-2 px-4 rounded-md hover:bg-gray-100" on:click={() => showClientDetails(client.id)}>
                        {client.nume}
                    </button>
                    <button class="bg-blue-500 text-white px-2 py-1 rounded-md" on:click={() => editClient(client)}>Edit</button>
                </li>
            {/each}
        </ul>
    </div>
    <div>
        <h2 class="text-2xl font-bold mb-4">Parts</h2>
        <input type="text" placeholder="Search Parts..." class="w-full p-2 border border-gray-300 rounded-md mb-2" bind:value={partSearch} />
        <ul class="divide-y divide-gray-200">
            {#each filteredParts as part (part.id)}
                <li class="py-2 flex justify-between items-center">
                    <span>{part.pn} - {part.descriere}</span>
                    <button class="bg-blue-500 text-white px-2 py-1 rounded-md" on:click={() => editPart(part)}>Edit</button>
                </li>
            {/each}
        </ul>
    </div>
</div>

{#if selectedClientDetails}
    <ClientDetailsPopup clientDetails={selectedClientDetails} on:close={() => selectedClientDetails = null} />
{/if}

{#if editingPart}
    <EditPartPopup part={editingPart} on:close={() => editingPart = null} on:partSaved={handlePartSaved} />
{/if}

{#if editingClient}
    <EditClientPopup client={editingClient} on:close={() => editingClient = null} on:clientSaved={handleClientSaved} />
{/if}