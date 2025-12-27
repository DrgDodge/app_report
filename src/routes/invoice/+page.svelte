<script lang="ts">
	let files: FileList;
	let statusMessage = '';
	let statusType: 'success' | 'error' = 'success';

	async function handleSubmit() {
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

		statusMessage = 'Generating invoice...';
		statusType = 'success';

		const formData = new FormData();
		formData.append('file', file);

		try {
			const response = await fetch('/api/invoice', {
				method: 'POST',
				body: formData
			});

			const result = await response.json();

			if (response.ok) {
				statusMessage = result.message;
				statusType = 'success';
				window.open(`/api/invoice/${result.invoice_id}/pdf`, '_blank');
			} else {
				throw new Error(result.message);
			}
		} catch (error: any) {
			statusMessage = `Error: ${error.message}`;
			statusType = 'error';
		}
	}
</script>

<div class="max-w-xl mx-auto my-5 p-5 border border-gray-300 bg-gray-50 font-sans rounded-lg">
	<h1 class="text-2xl font-bold mb-4">Invoice Generator</h1>

	<form on:submit|preventDefault={handleSubmit}>
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
			class="w-full bg-blue-600 text-white hover:bg-blue-700 font-semibold px-6 py-3 text-lg rounded-md"
		>
			Generate Invoice
		</button>
	</form>

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
</div>
