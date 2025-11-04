<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import type { Client } from './types';

    export let client: Client;

    const dispatch = createEventDispatcher();

    let updatedClient = { ...client };

    async function saveClient() {
        const res = await fetch(`/api/client/${updatedClient.id}`,
            {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(updatedClient)
            });

        if (res.ok) {
            dispatch('clientSaved', updatedClient);
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

<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white p-8 rounded-lg shadow-lg w-full max-w-2xl">
        <h2 class="text-2xl font-bold mb-5">Edit Client</h2>

        <form on:submit|preventDefault={saveClient}>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="flex flex-col">
                    <label for="nume" class="font-bold text-sm mb-1 text-gray-700">Nume Firma</label>
                    <input type="text" id="nume" bind:value={updatedClient.nume} class="w-full p-2 border border-gray-300 rounded-md" />
                </div>
                <div class="flex flex-col">
                    <label for="cui" class="font-bold text-sm mb-1 text-gray-700">CUI</label>
                    <input type="text" id="cui" bind:value={updatedClient.cui} class="w-full p-2 border border-gray-300 rounded-md" />
                </div>
                <div class="flex flex-col">
                    <label for="nr_reg_com" class="font-bold text-sm mb-1 text-gray-700">Nr. Reg. Com.</label>
                    <input type="text" id="nr_reg_com" bind:value={updatedClient.nr_reg_com} class="w-full p-2 border border-gray-300 rounded-md" />
                </div>
                <div class="flex flex-col">
                    <label for="iban" class="font-bold text-sm mb-1 text-gray-700">IBAN</label>
                    <input type="text" id="iban" bind:value={updatedClient.iban} class="w-full p-2 border border-gray-300 rounded-md" />
                </div>
                <div class="flex flex-col col-span-2">
                    <label for="adresa" class="font-bold text-sm mb-1 text-gray-700">Adresa</label>
                    <input type="text" id="adresa" bind:value={updatedClient.adresa} class="w-full p-2 border border-gray-300 rounded-md" />
                </div>
                <div class="flex flex-col col-span-2">
                    <label for="locatie" class="font-bold text-sm mb-1 text-gray-700">Locatie</label>
                    <input type="text" id="locatie" bind:value={updatedClient.locatie} class="w-full p-2 border border-gray-300 rounded-md" />
                </div>
            </div>

            <div class="flex justify-end gap-4 mt-5">
                <button type="button" on:click={close} class="bg-gray-300 text-gray-800 hover:bg-gray-400 font-semibold px-4 py-2 rounded-md">Anuleaza</button>
                <button type="submit" class="bg-blue-600 text-white hover:bg-blue-700 font-semibold px-4 py-2 rounded-md">Salveaza</button>
            </div>
        </form>
    </div>
</div>