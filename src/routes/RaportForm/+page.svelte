<script lang="ts">
	// --- Tipuri de date ---
	interface Piesa {
		pn: string;
		descriere: string;
		buc: number | null;
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
	}

	interface ClientSugestie {
		id: number;
		nume: string;
	}

	interface PiesaSugestie {
		pn: string;
		descriere: string;
	}

	// URL-ul API-ului tau Flask (schimba-l daca e cazul)
	const API_BASE_URL = 'http://backend:5000/api';

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
		locatie: '',
		solicitare_client: '',
		utilaj: '',
		serie: '',
		ore_funct: null,
		operatii_efectuate: '',
		observatii: '',
		manopera_ore: null,
		km_efectuati: null,
		nume_semnatura_client: ''
	});

	let pieseInlocuite = $state<Piesa[]>([]);
	let pieseNecesare = $state<Piesa[]>([]);

	let clientSugestii = $state<ClientSugestie[]>([]);
	let pieseSugestii = $state<PiesaSugestie[]>([]);
	let showClientSugestii = $state(false);
	let showPieseSugestii = $state(false);
	let activePieseIndex = $state<number | null>(null); // Tine minte pt ce rand cautam piese
	let activePieseTip = $state<'inlocuite' | 'necesare'>('inlocuite');

	let statusMesaj = $state('');
	let statusTip = $state<'succes' | 'eroare'>('succes');

	// --- Functii pentru liste dinamice ---
	function addPiesaInlocuita() {
		pieseInlocuite = [...pieseInlocuite, { pn: '', descriere: '', buc: 1 }];
	}
	function removePiesaInlocuita(index: number) {
		pieseInlocuite.splice(index, 1);
	}
	function addPiesaNecesara() {
		pieseNecesare = [...pieseNecesare, { pn: '', descriere: '', buc: 1 }];
	}
	function removePiesaNecesara(index: number) {
		pieseNecesare.splice(index, 1);
	}

	// --- Functii Autocomplete ---

	let clientDebounceTimer: number;
	async function handleClientInput(e: Event) {
		const input = e.target as HTMLInputElement;
		raport.client = input.value;
		raport.client_id = null; // Resetam ID-ul daca utilizatorul editeaza manual
		showClientSugestii = true;

		clearTimeout(clientDebounceTimer);
		if (raport.client.length < 1) {
			clientSugestii = [];
			return;
		}

		clientDebounceTimer = setTimeout(async () => {
			const res = await fetch(`${API_BASE_URL}/search/clienti?q=${raport.client}`);
			clientSugestii = await res.json();
		}, 300); // Asteapta 300ms inainte de a cauta
	}

	async function selectClient(sugestie: ClientSugestie) {
		raport.client = sugestie.nume;
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
					if (details.utilaj) raport.utilaj = details.utilaj;
					if (details.serie_utilaj) raport.serie = details.serie_utilaj;
				}
			} catch (error) {
				console.error('Failed to fetch client details:', error);
			}
		}
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

		activePieseIndex = index;
		activePieseTip = tip;
		showPieseSugestii = true;

		clearTimeout(pieseDebounceTimer);
		if (query.length < 2) {
			pieseSugestii = [];
			return;
		}
		pieseDebounceTimer = setTimeout(async () => {
			const res = await fetch(`${API_BASE_URL}/search/piese?q=${query}`);
			pieseSugestii = await res.json();
		}, 300);
	}

	function selectPiesa(sugestie: PiesaSugestie) {
		if (activePieseIndex === null) return;

		if (activePieseTip === 'inlocuite') {
			pieseInlocuite[activePieseIndex].pn = sugestie.pn;
			pieseInlocuite[activePieseIndex].descriere = sugestie.descriere;
		} else {
			pieseNecesare[activePieseIndex].pn = sugestie.pn;
			pieseNecesare[activePieseIndex].descriere = sugestie.descriere;
		}
		pieseSugestii = [];
		showPieseSugestii = false;
		activePieseIndex = null;
	}

	// --- Functie de Salvare ---
	async function handleSubmit() {
		statusMesaj = 'Se salveaza...';
		statusTip = 'succes';

		const dataToSubmit = {
			raport: raport,
			pieseInlocuite: pieseInlocuite,
			pieseNecesare: pieseNecesare
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
		</header>

	<form onsubmit|preventDefault={handleSubmit}>
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
				<div class="relative flex flex-col">
					<label for="client" class="font-bold text-sm mb-1 text-gray-700">Client</label>
					<input
						type="text"
						id="client"
						bind:value={raport.client}
						oninput={handleClientInput}
						onblur={() => setTimeout(() => (showClientSugestii = false), 200)}
						onfocus={() => (showClientSugestii = raport.client.length > 0)}
						autocomplete="off"
						class={inputClass}
					/>
					{#if showClientSugestii && clientSugestii.length > 0}
						<ul
							class="absolute top-full left-0 right-0 bg-white border border-gray-300 border-t-0 rounded-b-md shadow-lg z-10 max-h-52 overflow-y-auto"
						>
							{#each clientSugestii as sugestie (sugestie.id)}
								<div
									role="button"
									tabindex="0"
									class="px-3 py-2 cursor-pointer hover:bg-gray-100"
									onmousedown={() => selectClient(sugestie)}
									onkeydown={(e) => e.key === 'Enter' && selectClient(sugestie)}
								>
									{sugestie.nume}
								</div>
							{/each}
						</ul>
					{/if}
				</div>
				<div class="flex flex-col">
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
				<div class="flex flex-col">
					<label for="utilaj" class="font-bold text-sm mb-1 text-gray-700">Utilaj</label>
					<input type="text" id="utilaj" bind:value={raport.utilaj} class={inputClass} />
				</div>
				<div class="flex flex-col">
					<label for="serie" class="font-bold text-sm mb-1 text-gray-700">Serie</label>
					<input type="text" id="serie" bind:value={raport.serie} class={inputClass} />
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
				<div class="flex flex-col">
					<label for="observatii" class="font-bold text-sm mb-1 text-gray-700">OBS</label>
					<textarea id="observatii" rows="10" bind:value={raport.observatii} class={inputClass}></textarea>
				</div>
			</div>

			<div class="flex flex-col gap-4">
				<div class="piese-section">
					                    <div role="heading" aria-level="2" class="font-bold text-lg block mb-2">Piese inlocuite</div>
					                    <table class="w-full border-collapse">
					                        <thead class="bg-gray-100">
					                            <tr>
					                                <th class="border border-gray-300 p-1 text-left text-sm w-[30%]">P/N</th>
					                                <th class="border border-gray-300 p-1 text-left text-sm w-[50%]">Descriere</th>
					                                <th class="border border-gray-300 p-1 text-left text-sm w-[10%]">Buc</th>
					                                <th class="border border-gray-300 p-1 text-left text-sm w-[10%]"></th>
					                            </tr>
					                        </thead>						<tbody>
							{#each pieseInlocuite as piesa, i (i)}
								<tr>
									<td class="border border-gray-300 p-1 relative">
										<input
											type="text"
											bind:value={piesa.pn}
											                                            oninput={(e) => handlePieseInput(e, i, 'inlocuite')}
											                                            onblur={() => setTimeout(() => (showPieseSugestii = false), 200)}											onfocus={(e) => handlePieseInput(e, i, 'inlocuite')}
											class={inputClassTable}
										/>
										{#if showPieseSugestii && activePieseIndex === i && activePieseTip === 'inlocuite' && pieseSugestii.length > 0}
											<ul
												class="absolute top-full left-0 bg-white border border-gray-300 shadow-lg z-20 max-h-52 overflow-y-auto w-[300px]"
											>
												{#each pieseSugestii as sugestie (sugestie.pn)}
													<div
														role="button"
														tabindex="0"
														class="px-3 py-2 cursor-pointer hover:bg-gray-100"
														onmousedown={() => selectPiesa(sugestie)}
														onkeydown={(e) => e.key === 'Enter' && selectPiesa(sugestie)}
													>
														<strong class="font-medium">{sugestie.pn}</strong> - {sugestie.descriere}
													</div>
												{/each}
											</ul>
										{/if}
									</td>
									<td class="border border-gray-300 p-1">
										<input type="text" bind:value={piesa.descriere} class={inputClassTable} />
									</td>
									<td class="border border-gray-300 p-1">
										<input type="number" min="1" bind:value={piesa.buc} class={inputClassTable} />
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
								<th class="border border-gray-300 p-1 text-left text-sm w-[30%]">P/N</th>
								<th class="border border-gray-300 p-1 text-left text-sm w-[50%]">Descriere</th>
								<th class="border border-gray-300 p-1 text-left text-sm w-[10%]">Buc</th>
								<th class="border border-gray-300 p-1 text-left text-sm w-[10%]"></th>
							</tr>
						</thead>
						<tbody>
							{#each pieseNecesare as piesa, i (i)}
								<tr>
									<td class="border border-gray-300 p-1 relative">
										<input
											type="text"
											bind:value={piesa.pn}
											oninput={(e) => handlePieseInput(e, i, 'necesare')}
											onblur={() => setTimeout(() => (showPieseSugestii = false), 200)}
											onfocus={(e) => handlePieseInput(e, i, 'necesare')}
											class={inputClassTable}
										/>
										                                        {#if showPieseSugestii && activePieseIndex === i && activePieseTip === 'necesare' && pieseSugestii.length > 0}
										                                            <ul
										                                                class="absolute top-full left-0 bg-white border border-gray-300 shadow-lg z-20 max-h-52 overflow-y-auto w-[300px]"
										                                            >
										                                                {#each pieseSugestii as sugestie (sugestie.pn)}
										                                                    <div
										                                                        role="button"
										                                                        tabindex="0"
										                                                        class="px-3 py-2 cursor-pointer hover:bg-gray-100"
										                                                        onmousedown={() => selectPiesa(sugestie)}
										                                                        onkeydown={(e) => e.key === 'Enter' && selectPiesa(sugestie)}
										                                                    >
										                                                        <strong class="font-medium">{sugestie.pn}</strong> - {sugestie.descriere}
										                                                    </div>
										                                                {/each}
										                                            </ul>
										                                        {/if}									</td>
									<td class="border border-gray-300 p-1">
										<input type="text" bind:value={piesa.descriere} class={inputClassTable} />
									</td>
									<td class="border border-gray-300 p-1">
										<input type="number" min="1" bind:value={piesa.buc} class={inputClassTable} />
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
						onclick={addPiesaNecesara}>+ Adauga piesa</button>
										</div>
						
										<div class="grid grid-cols-2 gap-4 mt-auto">
											<div class="flex flex-col">
												<label for="manopera" class="font-bold text-sm mb-1 text-gray-700"
													>Manopera (ore)</label
												>
												<input
													type="number"
													step="0.5"
													id="manopera"
													bind:value={raport.manopera_ore}
													class={inputClass}
												/>
											</div>
											<div class="flex flex-col">
												<label for="km" class="font-bold text-sm mb-1 text-gray-700">Km efectuati</label>
												<input type="number" id="km" bind:value={raport.km_efectuati} class={inputClass} />
											</div>
										</div>
									</div>
								</div>
						
								<footer class="flex flex-col md:flex-row justify-between items-end gap-5 border-t border-gray-300 pt-5 mt-5">
									<div class="flex-grow flex flex-col w-full">
										<label for="semnatura" class="font-bold text-sm mb-1 text-gray-700"
											>CLIENT (nume, prenume, functie, semn., stampila)</label
										>
										<input
											type="text"
											id="semnatura"
											placeholder="Nume si prenume persoana de contact"
											bind:value={raport.nume_semnatura_client}
											class={inputClass}
										/>
									</div>
									<button
										type="submit"
										onclick={handleSubmit}
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
						</div>