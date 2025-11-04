<script lang="ts">
    export let clientDetails;
</script>

{#if clientDetails}
    <div class="p-4 border border-gray-200 rounded-lg">
        <h3 class="text-xl font-bold mb-2">{clientDetails.client.nume}</h3>
        <p><strong>CUI:</strong> {clientDetails.client.cui}</p>
        <p><strong>Adresa:</strong> {clientDetails.client.adresa}</p>
        <p><strong>Locatie:</strong> {clientDetails.client.locatie}</p>

        <h4 class="text-lg font-bold mt-4 mb-2">Utilaje</h4>
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
    </div>
{/if}