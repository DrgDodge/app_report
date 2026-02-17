<script lang="ts">
	import { onMount } from 'svelte';
    import { fly } from 'svelte/transition';
    import InvoiceHistory from './InvoiceHistory.svelte';

	// --- Interfaces ---
	interface InvoiceItem {
		name: string;
		quantity: number;
		price: number;
		total: number;
	}

	interface InvoiceData {
        id?: number; // Added optional ID
		invoice_number: string;
		invoice_date: string;
		client_name: string;
        supplier_name: string; // Added supplier_name
		client_address: string;
		client_cui: string;
		items: InvoiceItem[];
		total: number;
		lucrare: string;
	}

	interface Lucrare {
		id: number;
		name: string;
	}

	// --- State ---
	let files: FileList;
	let statusMessage = '';
	let statusType: 'success' | 'error' = 'success';
	
	let invoiceData = $state<InvoiceData | null>(null);
	let lucrari = $state<Lucrare[]>([]);
	let selectedLucrareId = $state<number | null>(null);
    let newLucrareName = $state('');
    let showAddLucrare = $state(false);
    let showHistory = $state(false);

	// --- Lifecycle ---
	onMount(async () => {
		await fetchLucrari();
	});

	async function fetchLucrari() {
		try {
			const res = await fetch('/api/lucrare');
			if (res.ok) {
				lucrari = await res.json();
			}
		} catch (error) {
			console.error('Error fetching lucrari:', error);
		}
	}

	// --- Handlers ---
	async function handleUpload() {
		if (!files || files.length === 0) {
			statusMessage = 'Please select a file.';
			statusType = 'error';
			return;
		}

		const file = files[0];
		if (file.type !== 'text/xml') {
			statusMessage = 'Please select an XML file.';
			statusType = 'error';
			return;
		}

		statusMessage = 'Parsing invoice...';
		statusType = 'success';

		const formData = new FormData();
		formData.append('file', file);

		try {
			const response = await fetch('/api/invoice/parse', {
				method: 'POST',
				body: formData
			});

			const result = await response.json();

			if (response.ok) {
				statusMessage = '';
				invoiceData = result.data;
                
                // Fetch next invoice number only if new (no ID)
                if (invoiceData && !invoiceData.id) {
                    try {
                        const numRes = await fetch('/api/invoice/last-number');
                        if (numRes.ok) {
                            const numData = await numRes.json();
                            if (numData.number !== null) {
                                invoiceData.invoice_number = (numData.number + 1).toString();
                            }
                        }
                    } catch (e) {
                        console.error("Failed to fetch last invoice number", e);
                    }
                }
			} else {
				throw new Error(result.message);
			}
		} catch (error: any) {
			statusMessage = `Error: ${error.message}`;
			statusType = 'error';
		}
	}

	async function handleGeneratePDF() {
		if (!invoiceData) return;
		statusMessage = 'Saving and Generating PDF...';
		statusType = 'success';

		try {
            // 1. Save Invoice to DB
            const saveRes = await fetch('/api/invoice/save', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(invoiceData)
            });

            if (!saveRes.ok) {
                const err = await saveRes.json();
                throw new Error(err.message || 'Failed to save invoice');
            }

            const saveData = await saveRes.json();
            if (invoiceData) invoiceData.id = saveData.id; // Update ID

            // 2. Save the last invoice number settings
            await fetch('/api/invoice/save-number', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ number: parseInt(invoiceData!.invoice_number) })
            });

            // 3. Generate PDF
			const response = await fetch('/api/invoice/pdf', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(invoiceData)
			});

			if (response.ok) {
				const blob = await response.blob();
				const url = window.URL.createObjectURL(blob);
				window.open(url, '_blank');
				statusMessage = 'Saved & PDF Generated successfully!';
                
                // Auto-increment number for next time if it was a new invoice
                // We don't reset invoiceData here, user might want to edit more.
			} else {
                const errorData = await response.json();
				throw new Error(errorData.message || 'Failed to generate PDF');
			}
		} catch (error: any) {
			statusMessage = `Error: ${error.message}`;
			statusType = 'error';
		}
	}

	function addItem() {
		if (!invoiceData) return;
		invoiceData.items = [...invoiceData.items, { name: '', quantity: 1, price: 0, total: 0 }];
	}

	function removeItem(index: number) {
		if (!invoiceData) return;
		invoiceData.items = invoiceData.items.filter((_, i) => i !== index);
	}
    
    function updateItemTotal(index: number) {
        if (!invoiceData) return;
        const item = invoiceData.items[index];
        item.total = item.quantity * item.price;
    }

    $effect(() => {
        if (invoiceData) {
            invoiceData.total = invoiceData.items.reduce((acc, item) => acc + item.total, 0);
        }
    });

	async function addNewLucrare() {
        if(!newLucrareName.trim()) return;
        try {
            const res = await fetch('/api/lucrare', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ name: newLucrareName })
            });
            if(res.ok) {
                await fetchLucrari();
                newLucrareName = '';
                showAddLucrare = false;
            }
        } catch(e) {
            console.error(e);
        }
    }

    function handleLucrareChange() {
        if (!invoiceData) return;
        const lucrare = lucrari.find(l => l.id === selectedLucrareId);
        if (lucrare) {
            invoiceData.lucrare = lucrare.name;
        } else {
            invoiceData.lucrare = '';
        }
    }

    // --- History Handlers ---
    async function loadInvoiceForEdit(id: number) {
        try {
            const res = await fetch(`/api/invoice/${id}`);
            if (res.ok) {
                invoiceData = await res.json();
                showHistory = false;
                
                // Try to match selectedLucrareId based on loaded name
                if (invoiceData && invoiceData.lucrare) {
                    const matched = lucrari.find(l => l.name === invoiceData!.lucrare);
                    if (matched) selectedLucrareId = matched.id;
                }
            } else {
                alert('Failed to load invoice details');
            }
        } catch (e) {
            console.error(e);
            alert('Error loading invoice');
        }
    }

    async function quickGeneratePDF(id: number) {
         // Load data first, then generate
         try {
            const res = await fetch(`/api/invoice/${id}`);
            if (res.ok) {
                const data = await res.json();
                const pdfRes = await fetch('/api/invoice/pdf', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                if (pdfRes.ok) {
                    const blob = await pdfRes.blob();
                    const url = window.URL.createObjectURL(blob);
                    window.open(url, '_blank');
                } else {
                    alert('Failed to generate PDF');
                }
            }
         } catch(e) {
             console.error(e);
             alert('Error generating PDF');
         }
    }

    const inputClass = "w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none";
    const inputClassTable = "w-full p-1 border border-gray-300 rounded-md focus:ring-1 focus:ring-blue-500 focus:border-transparent outline-none";

</script>

<div class="max-w-4xl mx-auto my-5 p-5 border border-gray-300 bg-gray-50 font-sans rounded-lg relative">
	<header class="relative text-center mb-5">
        <h1 class="text-3xl font-bold">Bon Consum Generator</h1>
        <div class="absolute top-0 right-0">
             <button type="button" onclick={() => showHistory = true} class="bg-gray-200 text-gray-800 px-4 py-2 rounded-md font-semibold hover:bg-gray-300">Istoric</button>
        </div>
    </header>

	{#if !invoiceData}
		<!-- Upload Section -->
		<div class="max-w-xl mx-auto mt-10">
			<form onsubmit={(e) => { e.preventDefault(); handleUpload(); }}>
				<div class="mb-4">
					<label for="xml-file" class="block text-sm font-medium text-gray-700 mb-2"
						>Upload XML Invoice File</label
					>
					<input
						type="file"
						id="xml-file"
						bind:files
						accept=".xml,text/xml"
						class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
					/>
				</div>

				<button
					type="submit"
					class="w-full bg-blue-600 text-white hover:bg-blue-700 font-semibold px-6 py-3 text-lg rounded-md transition-transform active:scale-95"
				>
					Parse Invoice
				</button>
			</form>
		</div>
	{:else}
		<!-- Editor Section -->
		<div class="flex flex-col gap-5">
			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				<div class="flex flex-col">
					<label for="inv_num" class="font-bold text-sm mb-1 text-gray-700">Invoice Number</label>
					<input type="text" id="inv_num" bind:value={invoiceData.invoice_number} class={inputClass} />
				</div>
				<div class="flex flex-col">
					<label for="inv_date" class="font-bold text-sm mb-1 text-gray-700">Date</label>
					<input type="text" id="inv_date" bind:value={invoiceData.invoice_date} class={inputClass} />
				</div>
                 <div class="flex flex-col md:col-span-2">
                    <label for="supplier" class="font-bold text-sm mb-1 text-gray-700">Furnizor (Client)</label>
                    <input type="text" id="supplier" bind:value={invoiceData.supplier_name} class={inputClass} />
                </div>
                <div class="flex flex-col md:col-span-2">
                     <label for="lucrare" class="font-bold text-sm mb-1 text-gray-700">Lucrare (Work)</label>
                     <div class="flex gap-2">
                        <select 
                            id="lucrare" 
                            bind:value={selectedLucrareId} 
                            onchange={handleLucrareChange}
                            class={inputClass}
                        >
                            <option value={null}>Select Lucrare...</option>
                            {#each lucrari as l}
                                <option value={l.id}>{l.name}</option>
                            {/each}
                        </select>
                        <button type="button" onclick={() => showAddLucrare = !showAddLucrare} class="bg-green-500 text-white px-3 py-2 rounded-md font-bold">+</button>
                     </div>
                     {#if showAddLucrare}
                        <div class="flex gap-2 mt-2" transition:fly={{ y: -5 }}>
                            <input type="text" bind:value={newLucrareName} placeholder="New Lucrare Name" class={inputClass} />
                            <button type="button" onclick={addNewLucrare} class="bg-blue-500 text-white px-3 py-2 rounded-md">Save</button>
                        </div>
                     {/if}
                </div>
			</div>

            <div class="border-t border-gray-300 pt-5">
                <h2 class="text-xl font-bold mb-3">Products</h2>
                <table class="w-full border-collapse">
                    <thead class="bg-gray-100">
                        <tr>
                            <th class="border border-gray-300 p-2 text-left w-10">#</th>
                            <th class="border border-gray-300 p-2 text-left">Name</th>
                            <th class="border border-gray-300 p-2 text-left w-24">Qty</th>
                            <th class="border border-gray-300 p-2 text-left w-28">Price</th>
                            <th class="border border-gray-300 p-2 text-left w-28">Total</th>
                            <th class="border border-gray-300 p-2 text-center w-16">Act</th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each invoiceData.items as item, i (i)}
                            <tr>
                                <td class="border border-gray-300 p-2 text-center">{i + 1}</td>
                                <td class="border border-gray-300 p-2">
                                    <input type="text" bind:value={item.name} class={inputClassTable} />
                                </td>
                                <td class="border border-gray-300 p-2">
                                    <input type="number" step="0.001" bind:value={item.quantity} oninput={() => updateItemTotal(i)} class={inputClassTable} />
                                </td>
                                <td class="border border-gray-300 p-2">
                                    <input type="number" step="0.01" bind:value={item.price} oninput={() => updateItemTotal(i)} class={inputClassTable} />
                                </td>
                                <td class="border border-gray-300 p-2 text-right">
                                    {item.total.toFixed(2)}
                                </td>
                                <td class="border border-gray-300 p-2 text-center">
                                    <button type="button" onclick={() => removeItem(i)} class="text-red-600 hover:text-red-800 font-bold">X</button>
                                </td>
                            </tr>
                        {/each}
                    </tbody>
                    <tfoot>
                        <tr>
                            <td colspan="4" class="text-right font-bold p-2">Total:</td>
                            <td class="text-right font-bold p-2">{invoiceData.total.toFixed(2)}</td>
                            <td></td>
                        </tr>
                    </tfoot>
                </table>
                <button type="button" onclick={addItem} class="mt-2 bg-green-100 text-green-800 px-4 py-2 rounded-md font-semibold hover:bg-green-200">+ Add Product</button>
            </div>

            <div class="flex gap-4 mt-5">
                <button type="button" onclick={() => invoiceData = null} class="bg-gray-500 text-white px-6 py-3 rounded-md hover:bg-gray-600">Cancel</button>
                <button type="button" onclick={handleGeneratePDF} class="flex-grow bg-blue-600 text-white px-6 py-3 rounded-md font-bold hover:bg-blue-700 text-lg">Save & Generate PDF</button>
            </div>

		</div>
	{/if}

	{#if statusMessage}
		<div
			class="mt-5 p-3 rounded-md text-center"
			class:bg-green-100={statusType === 'success'}
			class:text-green-800={statusType === 'success'}
			class:bg-red-100={statusType === 'error'}
			class:text-red-800={statusType === 'error'}
		>
			{statusMessage}
		</div>
	{/if}

    {#if showHistory}
        <InvoiceHistory 
            on:close={() => showHistory = false}
            on:edit={(e) => loadInvoiceForEdit(e.detail)}
            on:generate={(e) => quickGeneratePDF(e.detail)}
        />
    {/if}
</div>