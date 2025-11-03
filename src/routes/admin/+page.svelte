<script lang="ts">
    import { dev } from '$app/environment';
    import { onMount } from 'svelte';

    const API_BASE_URL = '/api';

    let initDbMessage = $state('');
    let initDbStatus = $state('idle');

    let backupDbMessage = $state('');
    let backupDbStatus = $state('idle');

    let companie = $state({
        nume: '',
        adresa: '',
        email: '',
        telefon: '',
        logo: ''
    });

    let updateCompanieMessage = $state('');
    let updateCompanieStatus = $state('idle');

    onMount(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/companie`);
            if (response.ok) {
                companie = await response.json();
            }
        } catch (error) {
            console.error('Failed to fetch company details:', error);
        }
    });

    async function initializeDatabase() {
        initDbMessage = 'Initializing database...';
        initDbStatus = 'idle';
        try {
            const response = await fetch(`${API_BASE_URL}/admin/init-db`, {
                method: 'POST',
            });
            if (response.ok) {
                try {
                    const result = await response.json();
                    initDbMessage = result.message;
                    initDbStatus = 'success';
                } catch (e) {
                    initDbMessage = 'Database initialized, but failed to parse response.';
                    initDbStatus = 'success';
                }
            } else {
                const errorText = await response.text();
                throw new Error(errorText);
            }
        } catch (error: any) {
            initDbMessage = `Error: ${error.message}`;
            initDbStatus = 'error';
        }
    }

    async function backupDatabase() {
        backupDbMessage = 'Creating database backup...';
        backupDbStatus = 'idle';
        try {
            const response = await fetch(`${API_BASE_URL}/admin/backup-db`, {
                method: 'GET',
            });
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `date_backup_${new Date().toISOString().split('T')[0]}.db`;
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
                backupDbMessage = 'Database backup created successfully.';
                backupDbStatus = 'success';
            } else {
                const errorText = await response.text();
                throw new Error(errorText);
            }
        } catch (error: any) {
            backupDbMessage = `Error: ${error.message}`;
            backupDbStatus = 'error';
        }
    }

    async function updateCompanie() {
        updateCompanieMessage = 'Se actualizeaza datele companiei...';
        updateCompanieStatus = 'idle';
        try {
            const response = await fetch(`${API_BASE_URL}/companie`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(companie)
            });
            const result = await response.json();
            if (response.ok) {
                updateCompanieMessage = result.message;
                updateCompanieStatus = 'success';
            } else {
                throw new Error(result.message);
            }
        } catch (error: any) {
            updateCompanieMessage = `Eroare: ${error.message}`;
            updateCompanieStatus = 'error';
        }
    }
</script>

<div class="max-w-4xl mx-auto my-5 p-5 border border-gray-300 bg-gray-50 font-sans rounded-lg">
    <h1 class="text-3xl font-bold mb-5">Admin Panel</h1>

    <div class="mb-8 p-4 border border-blue-200 bg-blue-50 rounded-md">
        <h2 class="text-xl font-semibold mb-3">Database Initialization</h2>
        <p class="text-gray-700 mb-4">This will re-create all tables in the database based on <code>schema.sql</code>. <strong class="text-red-600">All existing data will be lost.</strong> Use with caution!</p>
        <button
            onclick={initializeDatabase}
            class="bg-red-600 text-white hover:bg-red-700 font-semibold px-4 py-2 rounded-md"
        >
            Initialize Database
        </button>
        {#if initDbMessage}
            <p class="mt-3 text-sm {initDbStatus === 'success' ? 'text-green-600' : 'text-red-600'}">{initDbMessage}</p>
        {/if}
    </div>

    <div class="p-4 border border-green-200 bg-green-50 rounded-md">
        <h2 class="text-xl font-semibold mb-3">Database Backup</h2>
        <p class="text-gray-700 mb-4">This will download a backup of the current <code>date.db</code> file.</p>
        <button
            onclick={backupDatabase}
            class="bg-green-600 text-white hover:bg-green-700 font-semibold px-4 py-2 rounded-md"
        >
            Create Database Backup
        </button>
        {#if backupDbMessage}
            <p class="mt-3 text-sm {backupDbStatus === 'success' ? 'text-green-600' : 'text-red-600'}">{backupDbMessage}</p>
        {/if}
    </div>

    <div class="mt-8 p-4 border border-yellow-200 bg-yellow-50 rounded-md">
        <h2 class="text-xl font-semibold mb-3">Date Companie</h2>
        <form onsubmit|preventDefault={updateCompanie}>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="flex flex-col">
                    <label for="nume" class="font-bold text-sm mb-1 text-gray-700">Nume</label>
                    <input type="text" id="nume" bind:value={companie.nume} class="w-full p-2 border border-gray-300 rounded-md">
                </div>
                <div class="flex flex-col">
                    <label for="adresa" class="font-bold text-sm mb-1 text-gray-700">Adresa</label>
                    <input type="text" id="adresa" bind:value={companie.adresa} class="w-full p-2 border border-gray-300 rounded-md">
                </div>
                <div class="flex flex-col">
                    <label for="email" class="font-bold text-sm mb-1 text-gray-700">Email</label>
                    <input type="email" id="email" bind:value={companie.email} class="w-full p-2 border border-gray-300 rounded-md">
                </div>
                <div class="flex flex-col">
                    <label for="telefon" class="font-bold text-sm mb-1 text-gray-700">Telefon</label>
                    <input type="text" id="telefon" bind:value={companie.telefon} class="w-full p-2 border border-gray-300 rounded-md">
                </div>
                <div class="flex flex-col">
                    <label for="logo" class="font-bold text-sm mb-1 text-gray-700">Logo (ex: logo.png)</label>
                    <input type="text" id="logo" bind:value={companie.logo} class="w-full p-2 border border-gray-300 rounded-md">
                </div>
            </div>
            <button type="submit" class="mt-4 bg-blue-600 text-white hover:bg-blue-700 font-semibold px-4 py-2 rounded-md">
                Salveaza Datele Companiei
            </button>
            {#if updateCompanieMessage}
                <p class="mt-3 text-sm {updateCompanieStatus === 'success' ? 'text-green-600' : 'text-red-600'}">{updateCompanieMessage}</p>
            {/if}
        </form>
    </div>
</div>