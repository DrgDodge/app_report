<script lang="ts">
	import { writable } from 'svelte/store';
	import { fade, slide } from 'svelte/transition';
	import ClientPopup from './ClientPopup.svelte';
	import ReportHistory from './ReportHistory.svelte';

	// --- Data Types ---
	interface Piesa {
		id: number | null;
		pn: string;
		descriere: string;
		buc: number | null;
	}

	interface Manopera {
		tip: string;
		ore: number | null;
	}

	interface Raport {
		numar: string;
		tehnician: string;
		data: string;
		este_revizie: boolean;
		este_reparatie: boolean;
		este_constatare: boolean;
		este_garantie: boolean;
		client: string;
		client_id: number | null;
		cui: string;
		adresa: string;
		locatie: string;
		solicitare_client: string;
		utilaj: string;
		serie: string;
		ore_funct: number | null;
		operatii_efectuate: string;
		observatii: string;
		manopera_ore: number | null;
		km_efectuati: number | null;
		nume_semnatura_client: string;
		plecare: string;
		destinatie: string;
		retur: boolean;
	}

	// --- Component State ---
	let raport = $state<Raport>({
		numar: '',
		tehnician: 'Linu Adrian',
		data: new Date().toISOString().split('T')[0],
		este_revizie: false,
		este_reparatie: false,
		este_constatare: false,
		este_garantie: false,
		client: '',
		client_id: null,
		cui: '',
		adresa: '',
		locatie: '',
		solicitare_client: '',
		utilaj: '',
		serie: '',
		ore_funct: null,
		operatii_efectuate: '',
		observatii: '',
		manopera_ore: null,
		km_efectuati: null,
		nume_semnatura_client: '',
		plecare: 'Ploiesti',
		destinatie: '',
		retur: true
	});

	let pieseInlocuite = $state<Piesa[]>([]);
	let pieseNecesare = $state<Piesa[]>([]);
	let manoperaInregistrata = $state<Manopera[]>([]);

	let showClientPopup = $state(false);
	let showReportHistory = $state(false);
	let statusMesaj = $state('');
	let statusTip = $state<'succes' | 'eroare'>('succes');

	const API_BASE_URL = '/api';

	// --- Functions ---
	async function handleSubmit(event: Event) {
		event.preventDefault();
		statusMesaj = 'Se salveaza...';
		statusTip = 'succes';

		const dataToSubmit = {
			raport: raport,
			pieseInlocuite: pieseInlocuite,
			pieseNecesare: pieseNecesare,
			manopera: manoperaInregistrata
		};

		try {
			const response = await fetch(`${API_BASE_URL}/raport`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(dataToSubmit)
			});

			const result = await response.json();

			if (response.ok) {
				statusMesaj = `${result.message} (ID: ${result.raport_id})`;
				statusTip = 'succes';
				window.open(`${API_BASE_URL}/raport/${result.raport_id}/pdf`, '_blank');
			} else {
				throw new Error(result.message);
			}
		} catch (error: any) {
			statusMesaj = `Eroare: ${error.message}`;
			statusTip = 'eroare';
		}
	}
</script>

<div class="container mx-auto p-8 bg-gray-800 rounded-lg shadow-lg">
	<header class="flex justify-between items-center mb-8">
		<h1 class="text-3xl font-bold text-white">Create New Report</h1>
		<button
			on:click={() => (showReportHistory = true)}
			class="bg-gray-700 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded-lg transition-colors"
		>
			View History
		</button>
	</header>

	<form on:submit={handleSubmit} class="space-y-8">
        <!-- TODO: Add form sections here -->
		<footer class="flex justify-end pt-8">
			<button
				type="submit"
				class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition-colors"
			>
				Save Report & Generate PDF
			</button>
		</footer>

		{#if statusMesaj}
			<div
				class="mt-5 p-3 rounded-md text-center"
				class:bg-green-900={statusTip === 'succes'}
				class:text-green-300={statusTip === 'succes'}
				class:bg-red-900={statusTip === 'eroare'}
				class:text-red-300={statusTip === 'eroare'}
				in:fade
			>
				{statusMesaj}
			</div>
		{/if}
	</form>

	{#if showClientPopup}
		<div transition:fade={{ duration: 300 }}>
			<ClientPopup
				on:close={() => (showClientPopup = false)}
				on:clientSaved={(e) => {
					raport.client = e.detail.nume;
					raport.client_id = e.detail.id;
					raport.locatie = e.detail.locatie;
					raport.cui = e.detail.cui;
					showClientPopup = false;
				}}
			/>
		</div>
	{/if}

	{#if showReportHistory}
		<div transition:fade={{ duration: 300 }}>
			<ReportHistory
				on:close={() => (showReportHistory = false)}
				on:edit={async (e) => {
					const raportId = e.detail;
					const res = await fetch(`${API_BASE_URL}/raport/${raportId}`);
					if (res.ok) {
						const data = await res.json();
						raport = data.raport;
						pieseInlocuite = data.pieseInlocuite;
						pieseNecesare = data.pieseNecesare;
						manoperaInregistrata = data.manopera;
						showReportHistory = false;
					}
				}}
				on:delete={async (e) => {
					const raportId = e.detail;
					if (confirm('Are you sure you want to delete this report?')) {
						const res = await fetch(`${API_BASE_URL}/raport/${raportId}`, { method: 'DELETE' });
						if (res.ok) {
							showReportHistory = false;
						}
					}
				}}
				on:generate={(e) => {
					const raportId = e.detail;
					window.open(`${API_BASE_URL}/raport/${raportId}/pdf`, '_blank');
				}}
			/>
		</div>
	{/if}
</div>
