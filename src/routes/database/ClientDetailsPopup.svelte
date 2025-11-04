<script lang="ts">
    import { fly } from 'svelte/transition';
    import { createEventDispatcher, onMount } from 'svelte';
    import type { Client, Part } from './types';

    export let clientDetails: { client: Client, utilaje: any[] };

    const dispatch = createEventDispatcher();

    let clients: Client[] = [];
    let parts: Part[] = [];
    let clientSearch = '';
    let partSearch = '';

    onMount(async () => {
        const resClients = await fetch('/api/clients');
        clients = await resClients.json();

        const resParts = await fetch('/api/parts');
        parts = await resParts.json();
    });

    function close() {
        dispatch('close');
    }

    $: filteredClients = clients.filter(client => client.nume.toLowerCase().includes(clientSearch.toLowerCase()));
    $: filteredParts = parts.filter(part => part.pn.toLowerCase().includes(partSearch.toLowerCase()) || part.descriere.toLowerCase().includes(partSearch.toLowerCase()));

</script>

<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
     role="button" tabindex="0" on:click|self={close} on:keydown|self={e => e.key === 'Escape' && close()}>
    <div class="bg-white p-8 rounded-lg shadow-lg w-full max-w-4xl"
         in:fly={{ y: -50, duration: 300 }}
         out:fly={{ y: -50, duration: 300 }}>
        <button on:click={close} class="absolute top-4 right-4 text-gray-500 hover:text-gray-800">&times;</button>

        {#if clientDetails}
            <h2 class="text-2xl font-bold mb-4">{clientDetails.client.nume}</h2>

            <div class="grid grid-cols-2 gap-4">
                <div>
                    <h3 class="text-xl font-bold mb-2">Client Details</h3>
                    <p><strong>CUI:</strong> {clientDetails.client.cui}</p>
                    <p><strong>Adresa:</strong> {clientDetails.client.adresa}</p>
                    <p><strong>Locatie:</strong> {clientDetails.client.locatie}</p>
                </div>

            </div>

            <h3 class="text-xl font-bold mt-4 mb-2">Utilaje</h3>
            <ul class="divide-y divide-gray-200">
                {#each clientDetails.utilaje as utilaj (utilaj.id)}
                    <li class="py-2">
                        <p><strong>Utilaj:</strong> {utilaj.nume}</p>
                        <p><strong>Serie:</strong> {utilaj.serie}</p>

                        {#if utilaj.history && utilaj.history.length > 0}
                            <h5 class="text-md font-bold mt-2 mb-1">Istoric Ore Functionare</h5>
                            <ul class="list-disc list-inside">
                                {#each utilaj.history as historyItem (historyItem.id)}
                                    <li>{historyItem.data}: {historyItem.ore_funct} ore</li>
                                {/each}
                            </ul>
                        {/if}
                    </li>
                {/each}
            </ul>
        {/if}
    </div>
</div>