<script lang="ts">
    import { onMount } from 'svelte';
    import ClientDetails from './ClientDetails.svelte';

    let clients = [];
    let parts = [];
    let selectedClientDetails = null;

    onMount(async () => {
        const resClients = await fetch('/api/clients');
        clients = await resClients.json();

        const resParts = await fetch('/api/parts');
        parts = await resParts.json();
    });

    async function showClientDetails(clientId) {
        const res = await fetch(`/api/client/${clientId}/full_details`);
        selectedClientDetails = await res.json();
    }
</script>

<div class="grid grid-cols-2 gap-8">
    <div>
        <h2 class="text-2xl font-bold mb-4">Clients</h2>
        <ul class="divide-y divide-gray-200">
            {#each clients as client (client.id)}
                <button class="w-full text-left py-2 px-4 rounded-md hover:bg-gray-100" on:click={() => showClientDetails(client.id)}>
                    {client.nume}
                </button>
            {/each}
        </ul>
    </div>
    <div>
        <h2 class="text-2xl font-bold mb-4">Parts</h2>
        <ul class="divide-y divide-gray-200">
            {#each parts as part (part.id)}
                <li class="py-2">
                    {part.pn} - {part.descriere}
                </li>
            {/each}
        </ul>
    </div>
</div>

{#if selectedClientDetails}
    <div class="mt-8">
        <ClientDetails clientDetails={selectedClientDetails} />
    </div>
{/if}