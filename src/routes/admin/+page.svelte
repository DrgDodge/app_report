<script lang="ts">
    import { dev } from '$app/environment';
    import { onMount } from 'svelte';
    import BackupManager from './BackupManager.svelte';

    const API_BASE_URL = '/api';

    let initDbMessage = $state('');
    let initDbStatus = $state('idle');

    let backupDbMessage = $state('');
    let backupDbStatus = $state('idle');

    let showBackupManager = $state(false);

    let backupSchedule = $state({
        enabled: false,
        interval: 24,
        next_run_time: null,
    });
    let scheduleMessage = $state('');
    let scheduleStatus = $state('idle');
    let countdown = $state('');

    let companie = $state({
        nume: '',
        adresa: '',
        email: '',
        telefon: '',
        logo: ''
    });

    let updateCompanieMessage = $state('');
    let updateCompanieStatus = $state('idle');
    let countdownInterval: any;

    onMount(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/companie`);
            if (response.ok) {
                companie = await response.json();
            }
        } catch (error) {
            console.error('Failed to fetch company details:', error);
        }
        fetchBackupSchedule();

        return () => {
            if (countdownInterval) {
                clearInterval(countdownInterval);
            }
        };
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
            const result = await response.json();
            if (response.ok) {
                backupDbMessage = result.message;
                backupDbStatus = 'success';
            } else {
                throw new Error(result.message);
            }
        } catch (error: any) {
            backupDbMessage = `Error: ${error.message}`;
            backupDbStatus = 'error';
        }
    }

    function formatCountdown(finishDate: Date) {
        const now = new Date();
        const diff = finishDate.getTime() - now.getTime();

        if (diff <= 0) {
            return '00:00:00:00';
        }

        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((diff % (1000 * 60)) / 1000);

        return `${days.toString().padStart(2, '0')}:${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }

    async function fetchBackupSchedule() {
        try {
            const response = await fetch(`${API_BASE_URL}/admin/backup-schedule`);
            if (response.ok) {
                const data = await response.json();
                backupSchedule.enabled = data.enabled;
                if (data.interval) {
                    backupSchedule.interval = data.interval;
                }
                if (data.next_run_time) {
                    backupSchedule.next_run_time = new Date(data.next_run_time);
                    if (countdownInterval) {
                        clearInterval(countdownInterval);
                    }
                    countdownInterval = setInterval(() => {
                        countdown = formatCountdown(backupSchedule.next_run_time);
                    }, 1000);
                } else {
                    if (countdownInterval) {
                        clearInterval(countdownInterval);
                    }
                    countdown = '';
                }
            }
        } catch (error) {
            console.error('Failed to fetch backup schedule:', error);
        }
    }

    async function updateBackupSchedule() {
        scheduleMessage = 'Updating backup schedule...';
        scheduleStatus = 'idle';
        try {
            const response = await fetch(`${API_BASE_URL}/admin/backup-schedule`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(backupSchedule),
            });
            const result = await response.json();
            if (response.ok) {
                scheduleMessage = result.message;
                scheduleStatus = 'success';
                fetchBackupSchedule();
            } else {
                throw new Error(result.message);
            }
        } catch (error: any) {
            scheduleMessage = `Error: ${error.message}`;
            scheduleStatus = 'error';
        }
    }

    async function updateCompanie(event: Event) {
        event.preventDefault();
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

    <div class="mb-8 p-4 border border-green-200 bg-green-50 rounded-md">
        <h2 class="text-xl font-semibold mb-3">Database Backup</h2>
        <p class="text-gray-700 mb-4">Create a manual backup or manage existing backups.</p>
        <button
            onclick={backupDatabase}
            class="bg-green-600 text-white hover:bg-green-700 font-semibold px-4 py-2 rounded-md mr-4"
        >
            Create Manual Backup
        </button>
        <button
            onclick={() => showBackupManager = true}
            class="bg-blue-600 text-white hover:bg-blue-700 font-semibold px-4 py-2 rounded-md"
        >
            Manage Backups
        </button>
        {#if backupDbMessage}
            <p class="mt-3 text-sm {backupDbStatus === 'success' ? 'text-green-600' : 'text-red-600'}">{backupDbMessage}</p>
        {/if}
    </div>

    <div class="mb-8 p-4 border border-purple-200 bg-purple-50 rounded-md">
        <h2 class="text-xl font-semibold mb-3">Automatic Backups</h2>
        <div class="flex items-center gap-4">
            <label class="flex items-center gap-2">
                <input type="checkbox" bind:checked={backupSchedule.enabled} class="form-checkbox h-5 w-5 text-purple-600">
                <span>Enable Automatic Backups</span>
            </label>
            <label class="flex items-center gap-2">
                <span>Frequency (hours):</span>
                <input type="number" bind:value={backupSchedule.interval} min="1" class="p-2 border border-gray-300 rounded-md w-24">
            </label>
            <button
                onclick={updateBackupSchedule}
                class="bg-purple-600 text-white hover:bg-purple-700 font-semibold px-4 py-2 rounded-md"
            >
                Save Schedule
            </button>
        </div>
        {#if scheduleMessage}
            <p class="mt-3 text-sm {scheduleStatus === 'success' ? 'text-green-600' : 'text-red-600'}">{scheduleMessage}</p>
        {/if}
        {#if countdown}
            <p class="mt-3 text-sm text-gray-600">Next backup in: {countdown} (DD:HH:MM:SS)</p>
        {/if}
    </div>

    <div class="mt-8 p-4 border border-yellow-200 bg-yellow-50 rounded-md">
        <h2 class="text-xl font-semibold mb-3">Date Companie</h2>
        <form onsubmit={updateCompanie}>
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

<BackupManager bind:showModal={showBackupManager} on:closeModal={() => showBackupManager = false} />