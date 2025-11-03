<script lang="ts">
    const API_BASE_URL = 'http://127.0.0.1:5000/api';

    let initDbMessage = $state('');
    let initDbStatus: 'idle' | 'success' | 'error' = 'idle';

    let backupDbMessage = $state('');
    let backupDbStatus: 'idle' | 'success' | 'error' = 'idle';

    async function initializeDatabase() {
        initDbMessage = 'Initializing database...';
        initDbStatus = 'idle';
        try {
            const response = await fetch(`${API_BASE_URL}/admin/init-db`, {
                method: 'POST',
            });
            const result = await response.json();
            if (response.ok) {
                initDbMessage = result.message;
                initDbStatus = 'success';
            } else {
                throw new Error(result.message);
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
</script>

<div class="max-w-4xl mx-auto my-5 p-5 border border-gray-300 bg-gray-50 font-sans rounded-lg">
    <h1 class="text-3xl font-bold mb-5">Admin Panel</h1>

    <div class="mb-8 p-4 border border-blue-200 bg-blue-50 rounded-md">
        <h2 class="text-xl font-semibold mb-3">Database Initialization</h2>
        <p class="text-gray-700 mb-4">This will re-create all tables in the database based on <code>schema.sql</code>. <strong class="text-red-600">All existing data will be lost.</strong> Use with caution!</p>
        <button
            on:click={initializeDatabase}
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
            on:click={backupDatabase}
            class="bg-green-600 text-white hover:bg-green-700 font-semibold px-4 py-2 rounded-md"
        >
            Create Database Backup
        </button>
        {#if backupDbMessage}
            <p class="mt-3 text-sm {backupDbStatus === 'success' ? 'text-green-600' : 'text-red-600'}">{backupDbMessage}</p>
        {/if}
    </div>
</div>
