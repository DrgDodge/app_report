<script lang="ts">
    import { onMount } from "svelte";
    import { createEventDispatcher } from "svelte";

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
                console.error("Failed to fetch report history");
            }
        } catch (error) {
            console.error("Failed to fetch report history:", error);
        }
    });

    function editReport(id: number) {
        dispatch("edit", id);
    }

    function deleteReport(id: number) {
        dispatch("delete", id);
    }

    function generateReport(id: number) {
        dispatch("generate", id);
    }

</script>

<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg shadow-xl p-6 w-full max-w-4xl max-h-[80vh] flex flex-col">
        <div class="flex justify-between items-center border-b pb-3 mb-4">
            <h2 class="text-2xl font-bold">Istoric Rapoarte</h2>
            <button on:click={() => dispatch('close')} class="text-gray-500 hover:text-gray-800 text-2xl">&times;</button>
        </div>
        <div class="overflow-y-auto">
            <table class="w-full border-collapse">
                <thead class="bg-gray-100 sticky top-0">
                    <tr>
                        <th class="border border-gray-300 p-2 text-left text-sm">Nr. Raport</th>
                        <th class="border border-gray-300 p-2 text-left text-sm">Client</th>
                        <th class="border border-gray-300 p-2 text-left text-sm">Data</th>
                        <th class="border border-gray-300 p-2 text-left text-sm">Actiuni</th>
                    </tr>
                </thead>
                <tbody>
                    {#each rapoarte as raport (raport.id)}
                        <tr>
                            <td class="border border-gray-300 p-2">{raport.numar_raport}</td>
                            <td class="border border-gray-300 p-2">{raport.client_nume_text}</td>
                            <td class="border border-gray-300 p-2">{raport.data}</td>
                            <td class="border border-gray-300 p-2">
                                <button on:click={() => editReport(raport.id)} class="bg-blue-500 text-white px-2 py-1 rounded-md text-sm">Edit</button>
                                <button on:click={() => deleteReport(raport.id)} class="bg-red-500 text-white px-2 py-1 rounded-md text-sm">Delete</button>
                                <button on:click={() => generateReport(raport.id)} class="bg-green-500 text-white px-2 py-1 rounded-md text-sm">Generate</button>
                            </td>
                        </tr>
                    {/each}
                </tbody>
            </table>
        </div>
    </div>
</div>
