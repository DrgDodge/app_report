<script lang="ts">
    import { createEventDispatcher, onMount } from 'svelte';
    import { fade } from 'svelte/transition';

    const dispatch = createEventDispatcher();

    interface InvoiceSummary {
        id: number;
        invoice_number: string;
        invoice_date: string;
        supplier_name: string;
        total: number;
        lucrare: string;
    }

    let invoices: InvoiceSummary[] = [];
    let loading = true;
    let error = '';

    onMount(async () => {
        await fetchInvoices();
    });

    async function fetchInvoices() {
        loading = true;
        try {
            const res = await fetch('/api/invoices');
            if (res.ok) {
                invoices = await res.json();
            } else {
                error = 'Failed to load invoices';
            }
        } catch (e) {
            error = 'Error loading invoices';
            console.error(e);
        } finally {
            loading = false;
        }
    }

    function formatDate(dateStr: string) {
        if (!dateStr) return '-';
        return dateStr;
    }

    async function handleDelete(id: number) {
        if (!confirm('Are you sure you want to delete this invoice?')) return;
        
        try {
            const res = await fetch(`/api/invoice/${id}`, { method: 'DELETE' });
            if (res.ok) {
                invoices = invoices.filter(inv => inv.id !== id);
            } else {
                alert('Failed to delete invoice');
            }
        } catch (e) {
            console.error(e);
            alert('Error deleting invoice');
        }
    }
</script>

<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-5xl h-[80vh] flex flex-col" transition:fade>
        <div class="flex justify-between items-center p-4 border-b">
            <h2 class="text-xl font-bold text-gray-800">Istoric Bonuri de Consum</h2>
            <button class="text-gray-500 hover:text-gray-700" onclick={() => dispatch('close')}>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
            </button>
        </div>

        <div class="p-4 flex-grow overflow-y-auto">
            {#if loading}
                <div class="flex justify-center py-10">
                    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                </div>
            {:else if error}
                <div class="text-red-500 text-center py-10">{error}</div>
            {:else if invoices.length === 0}
                <div class="text-gray-500 text-center py-10">Nu exista bonuri salvate.</div>
            {:else}
                <table class="w-full text-left border-collapse">
                    <thead class="bg-gray-100 text-gray-600 uppercase text-xs">
                        <tr>
                            <th class="p-3 border-b">Nr.</th>
                            <th class="p-3 border-b">Data</th>
                            <th class="p-3 border-b">Furnizor (Client)</th>
                            <th class="p-3 border-b">Lucrare</th>
                            <th class="p-3 border-b text-right">Total</th>
                            <th class="p-3 border-b text-center">Actiuni</th>
                        </tr>
                    </thead>
                    <tbody class="text-sm">
                        {#each invoices as inv (inv.id)}
                            <tr class="hover:bg-gray-50 border-b">
                                <td class="p-3 font-medium">{inv.invoice_number}</td>
                                <td class="p-3">{formatDate(inv.invoice_date)}</td>
                                <td class="p-3">{inv.supplier_name || '-'}</td>
                                <td class="p-3">{inv.lucrare || '-'}</td>
                                <td class="p-3 text-right">{inv.total ? inv.total.toFixed(2) : '0.00'}</td>
                                <td class="p-3 flex justify-center gap-2">
                                    <button 
                                        class="bg-blue-100 text-blue-700 hover:bg-blue-200 px-3 py-1 rounded text-xs font-semibold"
                                        onclick={() => dispatch('edit', inv.id)}
                                    >
                                        Edit
                                    </button>
                                    <button 
                                        class="bg-green-100 text-green-700 hover:bg-green-200 px-3 py-1 rounded text-xs font-semibold"
                                        onclick={() => dispatch('generate', inv.id)}
                                    >
                                        PDF
                                    </button>
                                    <button 
                                        class="bg-red-100 text-red-700 hover:bg-red-200 px-3 py-1 rounded text-xs font-semibold"
                                        onclick={() => handleDelete(inv.id)}
                                    >
                                        Sterge
                                    </button>
                                </td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            {/if}
        </div>

        <div class="p-4 border-t bg-gray-50 rounded-b-lg flex justify-end">
            <button class="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300" onclick={() => dispatch('close')}>
                Inchide
            </button>
        </div>
    </div>
</div>