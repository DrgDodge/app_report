<script lang="ts">
	import ClientPopup from './ClientPopup.svelte';
	import ReportHistory from './ReportHistory.svelte';

	// --- Tipuri de date ---
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
			client: string; // Numele clientului (text)
			client_id: number | null; // ID-ul clientului (din DB)
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
	interface ClientSugestie {
		id: number;
		nume: string;
	}

	    interface PiesaSugestie {
			id: number;
			pn: string;
			descriere: string;
		}
	
	    interface UtilajSugestie {
	        id: number;
	        nume: string;
	        serie: string;
	    }
	// URL-ul API-ului tau Flask (schimba-l daca e cazul)
	const API_BASE_URL = '/api';

	// --- Starea componentei ---
	let raport = $state<Raport>({
		numar: '',
		tehnician: 'Linu Adrian', // Valoare pre-completata
		data: new Date().toISOString().split('T')[0], // Data de azi
		este_revizie: false,
		este_reparatie: false,
		este_constatare: false,
		este_garantie: false,
		client: '',
		client_id: null, // ID-ul clientului (din DB)
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

	let allClients = $state<ClientSugestie[]>([]);
	let allParts = $state<PiesaSugestie[]>([]);
	let clientSugestii = $state<ClientSugestie[]>([]);
	    	let utilajSugestii = $state<UtilajSugestie[]>([]);    let clientUtilaje = $state<UtilajSugestie[]>([]);
    let showClientUtilaje = $state(false);	let serieSugestii = $state<string[]>([]);
	let pieseSugestii = $state<PiesaSugestie[]>([]);
	let showClientSugestii = $state(false);
	let showUtilajSugestii = $state(false);
	    let showSerieSugestii = $state(false);
	    let showUtilajeList = $state(false);	let showPieseSugestii = $state(false);
	let activePieseIndex = $state<number | null>(null); // Tine minte pt ce rand cautam piese
	let activePieseTip = $state<'inlocuite' | 'necesare'>('inlocuite');

	let statusMesaj = $state('');
	let statusTip = $state<'succes' | 'eroare'>('succes');

	    let showClientPopup = $state(false);
	    let showReportHistory = $state(false);

	let descriereSugestii = $state<PiesaSugestie[]>([]);
	let showDescriereSugestii = $state(false);
	let activeDescriereIndex = $state<number | null>(null);
	let activeDescriereTip = $state<'inlocuite' | 'necesare'>('inlocuite');
	
	let destinatieSugestii = $state<string[]>([]);
	let showDestinatieSugestii = $state(false);

	async function handleDestinatieInput(e: Event) {
		const input = e.target as HTMLInputElement;
		raport.destinatie = input.value;
		showDestinatieSugestii = true;

		const res = await fetch(`${API_BASE_URL}/search/destinatii?q=${raport.destinatie}`);
		if (res.ok) {
			destinatieSugestii = await res.json();
		}
	}

	function selectDestinatie(sugestie: string) {
		raport.destinatie = sugestie;
		showDestinatieSugestii = false;
	}
	
	const tipuriManopera = [
		'Electrica',
		'Hidraulica',
		'Mecanica Motor',
		'Transmisii',
		'Mecanica Motor Garantie',
		'Diagnoza',
		'Pneumatica'
	];
	let manoperaSugestii = $state<string[]>([]);
	let showManoperaSugestii = $state(false);
	let activeManoperaIndex = $state<number | null>(null);

	    // --- Functii pentru liste dinamice ---
	    function addPiesaInlocuita() {
	        pieseInlocuite = [...pieseInlocuite, { id: null, pn: '', descriere: '', buc: 1 }];
	    }
	    function removePiesaInlocuita(index: number) {
	        pieseInlocuite.splice(index, 1);
	    }
	    function addPiesaNecesara() {
	        pieseNecesare = [...pieseNecesare, { id: null, pn: '', descriere: '', buc: 1 }];
	    }
	    function removePiesaNecesara(index: number) {
	        pieseNecesare.splice(index, 1);
	    }

		function addManopera() {
			manoperaInregistrata = [...manoperaInregistrata, { tip: '', ore: null }];
		}
		function removeManopera(index: number) {
			manoperaInregistrata.splice(index, 1);
		}

		function copyToNecesare(piesa: Piesa) {
			pieseNecesare = [...pieseNecesare, { ...piesa }];
		}

		function handleManoperaInput(e: Event, index: number) {
			const input = e.target as HTMLInputElement;
			const query = input.value;
			manoperaInregistrata[index].tip = query;
			showManoperaSugestii = true;
			activeManoperaIndex = index;

			if (query.length === 0) {
				manoperaSugestii = tipuriManopera;
			} else {
				manoperaSugestii = tipuriManopera.filter(t => t.toLowerCase().includes(query.toLowerCase()));
			}
		}

		function selectManopera(sugestie: string, index: number) {
			manoperaInregistrata[index].tip = sugestie;
			showManoperaSugestii = false;
		}

		$effect(() => {
			raport.manopera_ore = manoperaInregistrata.reduce((total, item) => total + (item.ore || 0), 0);
		});
	
	    // --- Functii Autocomplete ---
	
	    	import { onMount } from 'svelte';
	    	import { fade, fly } from 'svelte/transition';	
	        onMount(async () => {
	            try {
	                const res = await fetch(`${API_BASE_URL}/raport/last-number`);
	                if (res.ok) {
	                    const lastNumber = await res.json();
	                    if (lastNumber) {
	                        const number = parseInt(lastNumber.toString().split('-')[0]);
	                        if (!isNaN(number)) {
	                            raport.numar = `${number + 1}`;
	                        }
	                    }
	                }
	            } catch (error) {
	                console.error('Failed to fetch last report number:', error);
	            }
	        });
	let clientDebounceTimer: number;
	async function handleClientInput(e: Event) {
		const input = e.target as HTMLInputElement;
		raport.client = input.value;
		raport.nume_semnatura_client = input.value;
		raport.client_id = null; // Resetam ID-ul daca utilizatorul editeaza manual
		showClientSugestii = true;

		// Fetch all clients if not already fetched
		if (allClients.length === 0) {
			const res = await fetch(`${API_BASE_URL}/clients`);
			if (res.ok) {
				allClients = await res.json();
			}
		}

		clearTimeout(clientDebounceTimer);
		if (raport.client.length < 1) {
			clientSugestii = allClients; // Show all if input is empty
			return;
		}

		clientDebounceTimer = setTimeout(() => {
			clientSugestii = allClients.filter(c => c.nume.toLowerCase().includes(raport.client.toLowerCase()));
		}, 100);
	}

	async function selectClient(sugestie: ClientSugestie) {
		raport.client = sugestie.nume;
		raport.nume_semnatura_client = sugestie.nume;
		raport.client_id = sugestie.id;
		clientSugestii = [];
		showClientSugestii = false;

		// --- Populare automata a datelor clientului ---
		if (sugestie.id) {
			try {
				const res = await fetch(`${API_BASE_URL}/client/${sugestie.id}/details`);
				if (res.ok) {
					const details = await res.json();
					if (details.locatie) raport.locatie = details.locatie;
					if (details.cui) raport.cui = details.cui;
					if (details.adresa) raport.adresa = details.adresa;
					if (details.contact) raport.nume_semnatura_client = details.contact;
				}
			} catch (error) {
				console.error('Failed to fetch client details:', error);
			}
		}
	}

	let utilajDebounceTimer: number;
	async function handleUtilajInput(e: Event) {
		const input = e.target as HTMLInputElement;
		raport.utilaj = input.value;
		showUtilajSugestii = true;

		if (!raport.client_id) {
			utilajSugestii = [];
			return;
		}

		// Fetch utilaje for the client if not already fetched or if client has changed
		if (clientUtilaje.length === 0) {
			const res = await fetch(`${API_BASE_URL}/client/${raport.client_id}/utilaje`);
			if (res.ok) {
				clientUtilaje = await res.json();
			}
		}
		
		clearTimeout(utilajDebounceTimer);
		if (raport.utilaj.length < 1) {
			utilajSugestii = clientUtilaje; // Show all if input is empty
			return;
		}

		utilajDebounceTimer = setTimeout(async () => {
			utilajSugestii = clientUtilaje.filter(u => u.nume.toLowerCase().includes(raport.utilaj.toLowerCase()));
		}, 100);
	}

	function selectUtilaj(sugestie: UtilajSugestie) {
		raport.utilaj = sugestie.nume;
		raport.serie = sugestie.serie;
		utilajSugestii = [];
		showUtilajSugestii = false;
	}

	let serieDebounceTimer: number;
	let descriereDebounceTimer: number;
	async function handleSerieInput(e: Event) {
		const input = e.target as HTMLInputElement;
		raport.serie = input.value;
		showSerieSugestii = true;

		clearTimeout(serieDebounceTimer);
		if (raport.serie.length < 1) {
			serieSugestii = [];
			return;
		}

		serieDebounceTimer = setTimeout(async () => {
			const res = await fetch(`${API_BASE_URL}/search/serii?q=${raport.serie}&utilaj=${raport.utilaj}`);
			serieSugestii = await res.json();
		}, 300);
	}

	    function selectSerie(sugestie: string) {
	        raport.serie = sugestie;
	        serieSugestii = [];
	        showSerieSugestii = false;
	    }

		async function handleDescriereInput(e: Event, index: number, tip: 'inlocuite' | 'necesare') {
		const input = e.target as HTMLInputElement;
		const query = input.value;

		if (tip === 'inlocuite') {
			pieseInlocuite[index].descriere = query;
		} else {
			pieseNecesare[index].descriere = query;
		}

		showDescriereSugestii = true;

		if (allParts.length === 0) {
			const res = await fetch(`${API_BASE_URL}/parts`);
			if (res.ok) {
				allParts = await res.json();
			}
		}

		clearTimeout(descriereDebounceTimer);
		if (query.length < 1) {
			descriereSugestii = allParts;
			return;
		}

		descriereDebounceTimer = setTimeout(() => {
			descriereSugestii = allParts.filter(p => p.descriere.toLowerCase().includes(query.toLowerCase()));
		}, 100);
	}

	function selectDescriere(sugestie: PiesaSugestie) {
		if (activeDescriereIndex === null) return;

		const list = activeDescriereTip === 'inlocuite' ? pieseInlocuite : pieseNecesare;

		// Check if part with same id already exists
		if (list.some(p => p.id === sugestie.id && p.id !== null)) {
			alert('Aceasta piesa a fost deja adaugata.');
			return;
		}

		const newPiesa = { ...sugestie };
		if (newPiesa.pn && newPiesa.pn.startsWith('NO-')) {
			newPiesa.pn = '';
		}

		if (activeDescriereTip === 'inlocuite') {
			pieseInlocuite[activeDescriereIndex] = { ...pieseInlocuite[activeDescriereIndex], ...newPiesa };
		} else {
			pieseNecesare[activeDescriereIndex] = { ...pieseNecesare[activeDescriereIndex], ...newPiesa };
		}
		descriereSugestii = [];
		showDescriereSugestii = false;
		activeDescriereIndex = null;
	}
	
	let pieseDebounceTimer: number;
	async function handlePieseInput(e: Event, index: number, tip: 'inlocuite' | 'necesare') {
		const input = e.target as HTMLInputElement;
		const query = input.value;

		if (tip === 'inlocuite') {
			pieseInlocuite[index].pn = query;
		} else {
			pieseNecesare[index].pn = query;
		}

		showPieseSugestii = true;

		if (allParts.length === 0) {
			const res = await fetch(`${API_BASE_URL}/parts`);
			if (res.ok) {
				allParts = await res.json();
			}
		}

		clearTimeout(pieseDebounceTimer);
		if (query.length < 1) {
			pieseSugestii = allParts;
			return;
		}

		pieseDebounceTimer = setTimeout(() => {
			pieseSugestii = allParts.filter(p => p.pn.toLowerCase().includes(query.toLowerCase()) || p.descriere.toLowerCase().includes(query.toLowerCase()));
		}, 100);
	}

	function selectPiesa(sugestie: PiesaSugestie) {
		if (activePieseIndex === null) return;

		const list = activePieseTip === 'inlocuite' ? pieseInlocuite : pieseNecesare;

		// Check if part with same id already exists
		if (list.some(p => p.id === sugestie.id && p.id !== null)) {
			alert('Aceasta piesa a fost deja adaugata.');
			return;
		}

		const newPiesa = { ...sugestie };
		if (newPiesa.pn && newPiesa.pn.startsWith('NO-')) {
			newPiesa.pn = '';
		}

		if (activePieseTip === 'inlocuite') {
			pieseInlocuite[activePieseIndex] = { ...pieseInlocuite[activePieseIndex], ...newPiesa };
		} else {
			pieseNecesare[activePieseIndex] = { ...pieseNecesare[activePieseIndex], ...newPiesa };
		}
		pieseSugestii = [];
		showPieseSugestii = false;
		activePieseIndex = null;
	}

	// --- Functie de Salvare ---
	async function handleSubmit(event: Event) {
		event.preventDefault();

		// if (raport.client && !raport.client_id) {
		// 	alert("Clientul nu a fost selectat corect. Va rugam selectati un client din lista sau creati unul nou.");
		// 	return;
		// }

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
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(dataToSubmit)
			});

			const result = await response.json();

			if (response.ok) {
				statusMesaj = `${result.message} (ID: ${result.raport_id})`;
				statusTip = 'succes';
				// Optional: Deschide PDF-ul generat intr-un tab nou
				window.open(`${API_BASE_URL}/raport/${result.raport_id}/pdf`, '_blank');
			} else {
				throw new Error(result.message);
			}
		} catch (error: any) {
			statusMesaj = `Eroare: ${error.message}`;
			statusTip = 'eroare';
		}
	}

	// Helper pentru stil comun input/textarea
	const inputClass =
		'w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none';
	const inputClassTable =
		'w-full p-1 border border-gray-300 rounded-md focus:ring-1 focus:ring-blue-500 focus:border-transparent outline-none';
</script>

<div class="max-w-7xl mx-auto my-5 p-5 border border-gray-300 bg-gray-50 font-sans rounded-lg">
	<header class="relative text-center border-b-2 border-gray-800 pb-3 mb-5">
		<h1 class="text-3xl font-bold">RAPORT LUCRU</h1>
        <div class="absolute top-0 right-0">
            <button type="button" onclick={() => showReportHistory = true} class="bg-gray-200 text-gray-800 px-4 py-2 rounded-md">Istoric</button>
        </div>
		</header>

	<form onsubmit={handleSubmit}>
		<div class="grid grid-cols-1 md:grid-cols-[1fr_2fr_1fr] gap-4 mb-4">
			<div class="flex flex-col">
				<label for="nr_raport" class="font-bold text-sm mb-1 text-gray-700">Nr</label>
				<input type="text" id="nr_raport" bind:value={raport.numar} class={inputClass} />
			</div>
			<div class="flex flex-col">
				<label for="tehnician" class="font-bold text-sm mb-1 text-gray-700">Tehnician</label>
				<input type="text" id="tehnician" bind:value={raport.tehnician} class={inputClass} />
			</div>
			<div class="flex flex-col">
				<label for="data" class="font-bold text-sm mb-1 text-gray-700">Data</label>
				<input type="date" id="data" bind:value={raport.data} class={inputClass} />
			</div>
		</div>

		<div class="flex flex-wrap gap-x-5 gap-y-2 mb-5 border border-gray-200 p-3 rounded-md">
			<label class="flex items-center gap-2 cursor-pointer">
				<input type="checkbox" bind:checked={raport.este_revizie} class="h-4 w-4" /> REVIZIE
			</label>
			<label class="flex items-center gap-2 cursor-pointer">
				<input type="checkbox" bind:checked={raport.este_reparatie} class="h-4 w-4" /> REPARATIE
			</label>
			<label class="flex items-center gap-2 cursor-pointer">
				<input type="checkbox" bind:checked={raport.este_constatare} class="h-4 w-4" /> CONSTATARE
			</label>
			<label class="flex items-center gap-2 cursor-pointer">
				<input type="checkbox" bind:checked={raport.este_garantie} class="h-4 w-4" /> GARANTIE
			</label>
		</div>

		<div class="grid grid-cols-1 md:grid-cols-2 gap-5 mb-5 border-b border-gray-300 pb-5">
			<div class="flex flex-col gap-4">
				                <div class="relative flex items-end gap-2">
									<div class="flex-grow flex flex-col">
										<label for="client" class="font-bold text-sm mb-1 text-gray-700">Client</label>
										<input
											type="text"
											id="client"
											bind:value={raport.client}
											class={inputClass}
																			oninput={handleClientInput}							onblur={() => setTimeout(() => (showClientSugestii = false), 200)}
												onfocus={(e) => {
												showClientSugestii = true;
												handleClientInput(e);
											}}
											autocomplete="off"
										/>
										{#if showClientSugestii && clientSugestii.length > 0}
											<ul
												class="absolute top-full left-0 right-0 bg-white border border-gray-300 border-t-0 rounded-b-md shadow-lg z-10 max-h-52 overflow-y-auto"
												transition:fly={{ y: -5, duration: 200 }}
											>
												{#each clientSugestii as sugestie (sugestie.id)}
													<div
														role="button"
														tabindex="0"
														class="px-3 py-2 cursor-pointer hover:bg-gray-100"
																														onmousedown={() => selectClient(sugestie)}
																												>
																													{sugestie.nume}
																												</div>								{/each}
											</ul>
										{/if}
									</div>
									<button type="button" onclick={() => showClientPopup = true} class="bg-blue-500 text-white p-2 rounded-md">+</button>
								</div>
				                <div class="flex flex-col">
				                    <label for="cui" class="font-bold text-sm mb-1 text-gray-700">CUI</label>
				                    <input type="text" id="cui" bind:value={raport.cui} class={inputClass} />
				                </div>				<div class="flex flex-col">
					<label for="locatie" class="font-bold text-sm mb-1 text-gray-700">Locatie</label>
					<input type="text" id="locatie" bind:value={raport.locatie} class={inputClass} />
				</div>
				<div class="flex flex-col">
					<label for="solicitare" class="font-bold text-sm mb-1 text-gray-700"
						>Solicitare client</label
					>
					<textarea
						id="solicitare"
						rows="3"
						bind:value={raport.solicitare_client}
						class={inputClass}
					></textarea>
				</div>
			</div>
			<div class="flex flex-col gap-4">
				<div class="relative flex flex-col">
					<label for="utilaj" class="font-bold text-sm mb-1 text-gray-700">Utilaj</label>
					<div class="relative flex items-end gap-2">
						<input
							type="text"
							id="utilaj"
							bind:value={raport.utilaj}
							class={inputClass}
															oninput={handleUtilajInput}						onblur={() => setTimeout(() => (showUtilajSugestii = false), 200)}
								onfocus={(e) => {
									showUtilajSugestii = true;
									handleUtilajInput(e);
								}}
								autocomplete="off"
							/>
							{#if showUtilajSugestii && utilajSugestii.length > 0}
								<ul
									class="absolute top-full left-0 right-0 bg-white border border-gray-300 border-t-0 rounded-b-md shadow-lg z-10 max-h-52 overflow-y-auto"
									transition:fly={{ y: -5, duration: 200 }}
								>
									{#each utilajSugestii as sugestie (sugestie.id)}
										           <li>
																				<button
																					type="button"
																					class="w-full text-left px-3 py-2 cursor-pointer hover:bg-gray-100"
																					onclick={() => selectUtilaj(sugestie)}
																				>
																					{sugestie.nume}
																				</button>
																			</li>									{/each}
									</ul>
								{/if}
						<button type="button" onclick={async () => {
							if (raport.client_id) {
								const res = await fetch(`${API_BASE_URL}/client/${raport.client_id}/utilaje`);
								if (res.ok) {
									clientUtilaje = await res.json();
									showClientUtilaje = true;
								}
							}
						}} class="bg-blue-500 text-white p-2 rounded-md">...</button>
					</div>
					{#if showClientUtilaje}
						<ul class="absolute top-full left-0 right-0 bg-white border border-gray-300 border-t-0 rounded-b-md shadow-lg z-10 max-h-52 overflow-y-auto">
							{#each clientUtilaje as utilaj (utilaj.id)}
								<div role="button" tabindex="0" class="px-3 py-2 cursor-pointer hover:bg-gray-100" onmousedown={() => {
									raport.utilaj = utilaj.nume;
									raport.serie = utilaj.serie;
									showClientUtilaje = false;
								}}>
									{utilaj.nume} - {utilaj.serie}
								</div>
							{/each}
						</ul>
					{/if}
				</div>
				<div class="relative flex flex-col">
					<label for="serie" class="font-bold text-sm mb-1 text-gray-700">Serie</label>
					<input
						type="text"
						id="serie"
						bind:value={raport.serie}
						class={inputClass}
													oninput={handleSerieInput}						onblur={() => setTimeout(() => (showSerieSugestii = false), 200)}
						onfocus={() => {
							showSerieSugestii = true;
						}}
						autocomplete="off"
					/>
					{#if showSerieSugestii && serieSugestii.length > 0}
						<ul
							class="absolute top-full left-0 right-0 bg-white border border-gray-300 border-t-0 rounded-b-md shadow-lg z-10 max-h-52 overflow-y-auto"
							transition:fly={{ y: -5, duration: 200 }}
						>
							{#each serieSugestii as sugestie (sugestie)}
								<div
									role="button"
									tabindex="0"
									class="px-3 py-2 cursor-pointer hover:bg-gray-100"
																							onmousedown={() => selectSerie(sugestie)}
																							>
																								{sugestie}
																							</div>							{/each}
						</ul>
					{/if}
				</div>
				<div class="flex flex-col">
					<label for="ore_funct" class="font-bold text-sm mb-1 text-gray-700">Ore funct</label>
					<input type="number" id="ore_funct" bind:value={raport.ore_funct} class={inputClass} />
				</div>
			</div>
		</div>

		<div class="grid grid-cols-1 lg:grid-cols-[1.5fr_1fr] gap-5">
			<div class="flex flex-col gap-4">
				<div class="flex flex-col">
					<label for="operatii" class="font-bold text-sm mb-1 text-gray-700"
						>Operatii efectuate</label
					>
					<textarea
						id="operatii"
						rows="15"
						bind:value={raport.operatii_efectuate}
						class={inputClass}
					></textarea>
				</div>
			</div>

			<div class="flex flex-col gap-4">
				<div class="piese-section">
					                    <div role="heading" aria-level="2" class="font-bold text-lg block mb-2">Piese inlocuite</div>
					                    <table class="w-full border-collapse">
					                        <thead class="bg-gray-100">
					                            <tr>
					                                <th class="border border-gray-300 p-1 text-left text-sm w-[5%]">No.</th>
					                                <th class="border border-gray-300 p-1 text-left text-sm w-[30%]">P/N</th>
					                                <th class="border border-gray-300 p-1 text-left text-sm w-[45%]">Descriere</th>
					                                <th class="border border-gray-300 p-1 text-left text-sm w-[15%]">Buc</th>
					<th class="border border-gray-300 p-1 text-left text-sm w-[10%]"></th>
					                                <th class="border border-gray-300 p-1 text-left text-sm w-[10%]"></th>
					                            </tr>
					                        </thead>						<tbody>
							{#each pieseInlocuite as piesa, i (i)}
								<tr>
									<td class="border border-gray-300 p-1">{i + 1}</td>
									<td class="border border-gray-300 p-1 relative">
										<input
											type="text"
											bind:value={piesa.pn}
											class={inputClassTable}
											             onblur={() => setTimeout(() => (showPieseSugestii = false), 200)}											onfocus={(e) => {
												activePieseIndex = i;
												activePieseTip = 'inlocuite';
												showPieseSugestii = true;
												handlePieseInput(e, i, 'inlocuite');
											}}
										/>
										{#if showPieseSugestii && activePieseIndex === i && activePieseTip === 'inlocuite' && pieseSugestii.length > 0}
											<ul
												class="absolute top-full left-0 bg-white border border-gray-300 shadow-lg z-20 max-h-52 overflow-y-auto w-[300px]"
												transition:fly={{ y: -5, duration: 200 }}
											>
												{#each pieseSugestii as sugestie (sugestie.pn)}
													<div
														role="button"
														tabindex="0"
														class="px-3 py-2 cursor-pointer hover:bg-gray-100"
														onmousedown={() => selectPiesa(sugestie)}
													>
														{#if sugestie.pn && !sugestie.pn.startsWith('NO-')}
															<strong class="font-medium">{sugestie.pn}</strong> -
														{/if}
														{sugestie.descriere}
													</div>
																										{/each}
																									</ul>
																								{/if}
																							</td>
																							<td class="border border-gray-300 p-1 relative">
																																															<input type="text" bind:value={piesa.descriere} class={inputClassTable} 
																																					                                                                                                                                                                                                                                                                                            oninput={(e) => handleDescriereInput(e, i, 'inlocuite')}
																																					                                                                                                                                                                                                                                                                                            onblur={() => setTimeout(() => (showDescriereSugestii = false), 200)}
																																					                                                                                                                                                                                                                                                                                            																									                                                                                                                                                                                                                                                                                            																																					                                                                                                                                                                                                                                                                                            onfocus={(e) => { 
																																					                                                                                                                                                                                                                                                                                            																									                                                                                                                                                                                                                                                                                            																																					                                                                                                                                                                                                                                                                                            																									                                                                                                                                                                                                                                                                                                showDescriereSugestii = true; 
																																					                                                                                                                                                                                                                                                                                            																									                                                                                                                                                                                                                                                                                            																																					                                                                                                                                                                                                                                                                                            																									                                                                                                                                                                                                                                                                                                activeDescriereIndex = i;
																																					                                                                                                                                                                                                                                                                                            																									                                                                                                                                                                                                                                                                                            																																					                                                                                                                                                                                                                                                                                            																									                                                                                                                                                                                                                                                                                                activeDescriereTip = 'inlocuite';
																																					                                                                                                                                                                                                                                                                                            																									                                                                                                                                                                                                                                                                                            																																					                                                                                                                                                                                                                                                                                            																									                                                                                                                                                                                                                                                                                                handleDescriereInput(e, i, 'inlocuite');
																																					                                                                                                                                                                                                                                                                                            																									                                                                                                                                                                                                                                                                                            																																					                                                                                                                                                                                                                                                                                            																									                                                                                                                                                                                                                                                                                            }}																																					                                                                                                                                                                                                                                                    />														                                                                                                                        {#if showDescriereSugestii && activeDescriereIndex === i && activeDescriereTip === 'inlocuite' && descriereSugestii.length > 0}
																																					                                                                                                                            <ul
																																					                                                                                                                                class="absolute top-full left-0 bg-white border border-gray-300 shadow-lg z-20 max-h-52 overflow-y-auto w-[300px]"
																																					                                                                                                                            >
																																					                                                                                                                                                                                {#each descriereSugestii as sugestie (sugestie.pn)}
																																					                                                                                                                                                                                    <div
																																					                                                                                                                                                                                        role="button"
																																					                                                                                                                                                                                        tabindex="0"
																																					                                                                                                                                                                                        class="px-3 py-2 cursor-pointer hover:bg-gray-100"
																																					                                                                                                                                                                                        onmousedown={() => selectDescriere(sugestie)}
																																					                                                                                                                                                                                    >
																																					                                                                                                                                                                                        {#if sugestie.pn && !sugestie.pn.startsWith('NO-')}
																																					                                                                                                                                                                                            <strong class="font-medium">{sugestie.pn}</strong> -
																																					                                                                                                                                                                                        {/if}
																																					                                                                                                                                                                                        {sugestie.descriere}
																																					                                                                                                                                                                                    </div>
																																					                                                                                                                                                                                {/each}																																					                                                                                                                            </ul>
																																					                                                                                                                        {/if}																						</td>									<td class="border border-gray-300 p-1">
										<input type="number" step="0.1" bind:value={piesa.buc} class={inputClassTable} />
									</td>
									<td class="border border-gray-300 p-1">
										<button
											type="button"
											class="w-full bg-blue-100 text-blue-800 hover:bg-blue-200 font-semibold px-2 py-1 rounded-md"
											onclick={() => copyToNecesare(piesa)}>+</button
										>
									</td>
									<td class="border border-gray-300 p-1">
										<button
											type="button"
											class="w-full bg-red-100 text-red-800 hover:bg-red-200 font-semibold px-2 py-1 rounded-md"
											onclick={() => removePiesaInlocuita(i)}>X</button
										>
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
					<button
						type="button"
						class="bg-green-100 text-green-800 hover:bg-green-200 font-semibold px-2 py-1 rounded-md mt-2"
						onclick={addPiesaInlocuita}>+ Adauga piesa</button
					>
				</div>
                <div class="piese-section">
                    <div role="heading" aria-level="2" class="font-bold text-lg block mb-2">Necesar piese</div>
                    <table class="w-full border-collapse">
                        <thead class="bg-gray-100">
                            <tr>
                                <th class="border border-gray-300 p-1 text-left text-sm w-[5%]">No.</th>
                                <th class="border border-gray-300 p-1 text-left text-sm w-[30%]">P/N</th>
                                <th class="border border-gray-300 p-1 text-left text-sm w-[45%]">Descriere</th>
                                <th class="border border-gray-300 p-1 text-left text-sm w-[15%]">Buc</th>
                                <th class="border border-gray-300 p-1 text-left text-sm w-[10%]"></th>
                            </tr>
                        </thead>
                        <tbody>
                            {#each pieseNecesare as piesa, i (i)}
                                <tr>
                                    <td class="border border-gray-300 p-1">{i + 1}</td>
                                    <td class="border border-gray-300 p-1 relative">
                                        <input
                                            type="text"
                                            bind:value={piesa.pn}
                                            class={inputClassTable}
                                            onblur={() => setTimeout(() => (showPieseSugestii = false), 200)}
                                            oninput={(e) => handlePieseInput(e, i, 'necesare')}
                                            onfocus={(e) => {
                                                activePieseIndex = i;
                                                activePieseTip = 'necesare';
                                                showPieseSugestii = true;
                                                handlePieseInput(e, i, 'necesare');
                                            }}
                                        />
                                        {#if showPieseSugestii && activePieseIndex === i && activePieseTip === 'necesare' && pieseSugestii.length > 0}
                                            <ul
                                                class="absolute top-full left-0 bg-white border border-gray-300 shadow-lg z-20 max-h-52 overflow-y-auto w-[300px]"
                                            >
                                                {#each pieseSugestii as sugestie (sugestie.id)}
                                                    <div
                                                        role="button"
                                                        tabindex="0"
                                                        class="px-3 py-2 cursor-pointer hover:bg-gray-100"
                                                        onmousedown={() => selectPiesa(sugestie)}
                                                    >
                                                        {#if sugestie.pn && !sugestie.pn.startsWith('NO-')}
                                                            <strong class="font-medium">{sugestie.pn}</strong> -
                                                        {/if}
                                                        {sugestie.descriere}
                                                    </div>
                                                {/each}
                                            </ul>
                                        {/if}
                                    </td>
                                    <td class="border border-gray-300 p-1 relative">
                                        <input type="text" bind:value={piesa.descriere} class={inputClassTable} 
                                                                                oninput={(e) => handleDescriereInput(e, i, 'necesare')}
                                                                                onblur={() => setTimeout(() => (showDescriereSugestii = false), 200)}
                                                                                onfocus={(e) => { 
                                                                                    showDescriereSugestii = true; 
                                                                                    activeDescriereIndex = i;
                                                                                    activeDescriereTip = 'necesare';
                                                                                    handleDescriereInput(e, i, 'necesare');
                                                                                }}
                                        />
                                        {#if showDescriereSugestii && activeDescriereIndex === i && activeDescriereTip === 'necesare' && descriereSugestii.length > 0}
                                            <ul
                                                class="absolute top-full left-0 bg-white border border-gray-300 shadow-lg z-20 max-h-52 overflow-y-auto w-[300px]"
                                            >
                                                {#each descriereSugestii as sugestie (sugestie.id)}
                                                    <div
                                                        role="button"
                                                        tabindex="0"
                                                        class="px-3 py-2 cursor-pointer hover:bg-gray-100"
                                                        onmousedown={() => selectDescriere(sugestie)}
                                                    >
                                                        {#if sugestie.pn && !sugestie.pn.startsWith('NO-')}
                                                            <strong class="font-medium">{sugestie.pn}</strong> -
                                                        {/if}
                                                        {sugestie.descriere}
                                                    </div>
                                                {/each}
                                            </ul>
                                        {/if}
                                    </td>
                                    <td class="border border-gray-300 p-1">
                                        <input type="number" step="0.1" bind:value={piesa.buc} class={inputClassTable} />
                                    </td>
                                    <td class="border border-gray-300 p-1">
                                        <button
                                            type="button"
                                            class="w-full bg-red-100 text-red-800 hover:bg-red-200 font-semibold px-2 py-1 rounded-md"
                                            onclick={() => removePiesaNecesara(i)}>X</button
                                        >
                                    </td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                    <button
                        type="button"
                        class="bg-green-100 text-green-800 hover:bg-green-200 font-semibold px-2 py-1 rounded-md mt-2"
                        onclick={addPiesaNecesara}>+ Adauga piesa</button
                    >
                </div>
			</div>
		</div>

		<div class="mt-5">
			<table class="w-full border-collapse border border-gray-300">
				<tbody>
					<tr>
						<td class="border border-gray-300 p-2 align-top w-1/2">
							<div class="flex flex-col">
								<label for="observatii" class="font-bold text-sm mb-1 text-gray-700">OBS</label>
								<textarea id="observatii" rows="10" bind:value={raport.observatii} class={inputClass}></textarea>
							</div>
						</td>
						<td class="border border-gray-300 p-2 align-top w-1/2">
							<div class="piese-section">
								<div role="heading" aria-level="2" class="font-bold text-lg block mb-2">Manopera</div>
								<table class="w-full border-collapse">
									<thead class="bg-gray-100">
										<tr>
											<th class="border border-gray-300 p-1 text-left text-sm w-[70%]">Tip Manopera</th>
											<th class="border border-gray-300 p-1 text-left text-sm w-[20%]">Ore</th>
											<th class="border border-gray-300 p-1 text-left text-sm w-[10%]"></th>
										</tr>
									</thead>
									<tbody>
										{#each manoperaInregistrata as item, i (i)}
											<tr>
												<td class="border border-gray-300 p-1 relative">
													<input
														type="text"
														bind:value={item.tip}
														class={inputClassTable}
														oninput={(e) => handleManoperaInput(e, i)}
														onfocus={(e) => {
															showManoperaSugestii = true;
															activeManoperaIndex = i;
															handleManoperaInput(e, i);
														}}
														onblur={() => setTimeout(() => (showManoperaSugestii = false), 200)}
													/>
													{#if showManoperaSugestii && activeManoperaIndex === i && manoperaSugestii.length > 0}
														<ul
															class="absolute top-full left-0 bg-white border border-gray-300 shadow-lg z-20 max-h-52 overflow-y-auto w-[300px]"
														>
															{#each manoperaSugestii as sugestie (sugestie)}
																<div
																	role="button"
																	tabindex="0"
																	class="px-3 py-2 cursor-pointer hover:bg-gray-100"
																	onmousedown={() => selectManopera(sugestie, i)}
																>
																	{sugestie}
																</div>
															{/each}
														</ul>
													{/if}
												</td>
												<td class="border border-gray-300 p-1">
													<input type="number" step="0.5" bind:value={item.ore} class={inputClassTable} />
												</td>
												<td class="border border-gray-300 p-1">
													<button
														type="button"
														class="w-full bg-red-100 text-red-800 hover:bg-red-200 font-semibold px-2 py-1 rounded-md"
														onclick={() => removeManopera(i)}>X</button
													>
												</td>
											</tr>
										{/each}
									</tbody>
								</table>
								<button
									type="button"
									class="bg-green-100 text-green-800 hover:bg-green-200 font-semibold px-2 py-1 rounded-md mt-2"
									onclick={addManopera}>+ Adauga manopera</button
								>
							</div>
						</td>
					</tr>
				</tbody>
			</table>
		</div>

		<div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-5 border-t border-gray-300 pt-5">
			<div class="flex flex-col">
				<label for="plecare" class="font-bold text-sm mb-1 text-gray-700">Plecare</label>
				<input type="text" id="plecare" bind:value={raport.plecare} class={inputClass} />
			</div>
			<div class="flex flex-col relative">
				<label for="destinatie" class="font-bold text-sm mb-1 text-gray-700">Destinatie</label>
				<input
					type="text"
					id="destinatie"
					bind:value={raport.destinatie}
					class={inputClass}
					oninput={handleDestinatieInput}
					onblur={() => setTimeout(() => (showDestinatieSugestii = false), 200)}
					onfocus={handleDestinatieInput}
					autocomplete="off"
				/>
				{#if showDestinatieSugestii && destinatieSugestii.length > 0}
					<ul class="absolute top-full left-0 right-0 bg-white border border-gray-300 border-t-0 rounded-b-md shadow-lg z-10 max-h-52 overflow-y-auto">
						{#each destinatieSugestii as sugestie (sugestie)}
							<div
								role="button"
								tabindex="0"
								class="px-3 py-2 cursor-pointer hover:bg-gray-100"
								onmousedown={() => selectDestinatie(sugestie)}
							>
								{sugestie}
							</div>
						{/each}
					</ul>
				{/if}
			</div>
			<div class="flex items-end gap-4">
				<div class="flex-grow">
					<label for="km" class="font-bold text-sm mb-1 text-gray-700">Km efectuati</label>
					<input type="number" id="km" bind:value={raport.km_efectuati} class={inputClass} />
				</div>
				<div class="flex items-center gap-2 pb-2">
					<input type="checkbox" id="retur" bind:checked={raport.retur} class="h-4 w-4" />
					<label for="retur" class="font-bold text-sm text-gray-700">Retur</label>
				</div>
			</div>
		</div>

		<footer class="flex flex-col md:flex-row justify-between items-end gap-5 border-t border-gray-300 pt-5 mt-5">
			<div class="flex-grow flex flex-col w-full relative">
				<label for="semnatura" class="font-bold text-sm mb-1 text-gray-700"
					>CLIENT (nume, prenume, functie, semn., stampila)</label
				>
				<input
					type="text"
					id="semnatura"
					placeholder="Nume si prenume persoana de contact"
					bind:value={raport.nume_semnatura_client}
					class={inputClass}
					readonly
				/>
							</div>
			<button
				type="submit"
				class="w-full md:w-auto bg-blue-600 text-white hover:bg-blue-700 font-semibold px-6 py-3 text-lg rounded-md h-fit"
			>
				Salveaza Raport si Genereaza PDF
			</button>
		</footer>

		{#if statusMesaj}
			<div
				class="mt-5 p-3 rounded-md text-center"
				class:bg-green-100={statusTip === 'succes'}
				class:text-green-800={statusTip === 'succes'}
				class:bg-red-100={statusTip === 'eroare'}
				class:text-red-800={statusTip === 'eroare'}
			>
				{statusMesaj}
			</div>
		{/if}
	</form>

	{#if showClientPopup}
		<div transition:fly={{ y: -10, duration: 300 }}>
		                        <ClientPopup on:close={() => { showClientPopup = false; }} on:clientSaved={(e) => {		        raport.client = e.detail.nume;
		        raport.client_id = e.detail.id;
		        raport.locatie = e.detail.locatie;
		        raport.cui = e.detail.cui;
		        showClientPopup = false;
		    }} />
		</div>
	{/if}
		
		{#if showReportHistory}
		<div transition:fly={{ y: -10, duration: 300 }}>
		    <ReportHistory 
		        on:close={() => { showReportHistory = false; }}
		                on:edit={async (e) => {
		                    const raportId = e.detail;
		                    const res = await fetch(`${API_BASE_URL}/raport/${raportId}`);
		                    if(res.ok) {
		                        		                		                const data = await res.json();
		                        		                		                raport = data.raport;
		                        		                
		                        		                						data.pieseInlocuite.forEach(p => {
		                        		                							if (p.pn && p.pn.startsWith('NO-')) {
		                        		                								p.pn = '';
		                        		                							}
		                        		                						});
		                        		                		                pieseInlocuite = data.pieseInlocuite;
		                        		                
		                        		                						data.pieseNecesare.forEach(p => {
		                        		                							if (p.pn && p.pn.startsWith('NO-')) {
		                        		                								p.pn = '';
		                        		                							}
		                        		                						});
		                        		                		                pieseNecesare = data.pieseNecesare;
		                        		                
		                        		                		                manoperaInregistrata = data.manopera;
		                        		                		                showReportHistory = false;		                    }
		                }}		        on:delete={async (e) => {
		            const raportId = e.detail;
		            if(confirm('Sunteti sigur ca doriti sa stergeti acest raport?')){
		                const res = await fetch(`${API_BASE_URL}/raport/${raportId}`, { method: 'DELETE' });
		                if(res.ok){
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
<style>
	button {
		transition: transform 0.1s ease-in-out;
	}
	button:hover {
		transform: scale(1.05);
	}
	button:active {
		transform: scale(0.95);
	}
</style>