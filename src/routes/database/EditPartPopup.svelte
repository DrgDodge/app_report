<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import type { Part } from './types';

    export let part: Part;

    const dispatch = createEventDispatcher();

    let updatedPart = { ...part };

    async function savePart() {
        const res = await fetch(`/api/part/${updatedPart.id}`,
            {
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

<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white p-8 rounded-lg shadow-lg w-full max-w-2xl">
        <h2 class="text-2xl font-bold mb-5">Edit Part</h2>

        <form on:submit|preventDefault={savePart}>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="flex flex-col">
                    <label for="pn" class="font-bold text-sm mb-1 text-gray-700">P/N</label>
                    <input type="text" id="pn" bind:value={updatedPart.pn} class="w-full p-2 border border-gray-300 rounded-md" />
                </div>
                <div class="flex flex-col">
                    <label for="descriere" class="font-bold text-sm mb-1 text-gray-700">Descriere</label>
                    <input type="text" id="descriere" bind:value={updatedPart.descriere} class="w-full p-2 border border-gray-300 rounded-md" />
                </div>
            </div>

            <div class="flex justify-end gap-4 mt-5">
                <button type="button" on:click={close} class="bg-gray-300 text-gray-800 hover:bg-gray-400 font-semibold px-4 py-2 rounded-md">Anuleaza</button>
                <button type="submit" class="bg-blue-600 text-white hover:bg-blue-700 font-semibold px-4 py-2 rounded-md">Salveaza</button>
            </div>
        </form>
    </div>
</div>