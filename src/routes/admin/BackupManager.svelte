<script lang="ts">
    import { onMount } from 'svelte';

    const API_BASE_URL = '/api';

    let backups = $state<any[]>([]);
    let searchTerm = $state('');
    let message = $state('');
    let messageStatus = $state('idle');
    let fileInput: HTMLInputElement;

    let { showModal } = $props();

    let filteredBackups = $derived(backups.filter(b => b.filename.toLowerCase().includes(searchTerm.toLowerCase())));

    onMount(() => {
        if (showModal) {
            fetchBackups();
        }
    });

    $effect(() => {
        if (showModal) {
            fetchBackups();
        }
    });

    async function fetchBackups() {
        try {
            const response = await fetch(`${API_BASE_URL}/admin/backups`);
            if (response.ok) {
                backups = await response.json();
            } else {
                const result = await response.json();
                throw new Error(result.message);
            }
        } catch (error: any) {
            message = `Error: ${error.message}`;
            messageStatus = 'error';
        }
    }

    async function deleteBackup(filename: string) {
        if (!confirm(`Are you sure you want to delete ${filename}?`)) {
            return;
        }
        try {
            const response = await fetch(`${API_BASE_URL}/admin/backups/${filename}`, {
                method: 'DELETE',
            });
            const result = await response.json();
            if (response.ok) {
                message = result.message;
                messageStatus = 'success';
                fetchBackups();
            } else {
                throw new Error(result.message);
            }
        } catch (error: any) {
            message = `Error: ${error.message}`;
            messageStatus = 'error';
        }
    }

    async function restoreBackup(filename: string) {
        if (!confirm(`Are you sure you want to restore from ${filename}? This will overwrite the current database.`)) {
            return;
        }
        try {
            const response = await fetch(`${API_BASE_URL}/admin/restore-backup`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ filename }),
            });
            const result = await response.json();
            if (response.ok) {
                message = result.message;
                messageStatus = 'success';
            } else {
                throw new Error(result.message);
            }
        } catch (error: any) {
            message = `Error: ${error.message}`;
            messageStatus = 'error';
        }
    }
    async function downloadBackup(filename: string) {
        try {
            const response = await fetch(`${API_BASE_URL}/admin/backups/${filename}`);
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            } else {
                const result = await response.json();
                throw new Error(result.message);
            }
        } catch (error: any) {
            message = `Error: ${error.message}`;
            messageStatus = 'error';
        }
    }

    async function uploadBackup(event: Event) {
        const input = event.target as HTMLInputElement;
        if (!input.files || input.files.length === 0) {
            return;
        }
        const file = input.files[0];
        const formData = new FormData();
        formData.append('backup', file);

        try {
            const response = await fetch(`${API_BASE_URL}/admin/upload-backup`, {
                method: 'POST',
                body: formData,
            });
            const result = await response.json();
            if (response.ok) {
                message = result.message;
                messageStatus = 'success';
                fetchBackups();
            } else {
                throw new Error(result.message);
            }
        } catch (error: any) {
            message = `Error: ${error.message}`;
            messageStatus = 'error';
        }
    }

    function formatBytes(bytes: number, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }
</script>

{#if showModal}
<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg shadow-lg p-6 w-full max-w-4xl">
        <div class="flex justify-between items-center mb-4">
            <h2 class="text-2xl font-bold">Backup Manager</h2>
            <button onclick={() => showModal = false} class="text-gray-500 hover:text-gray-800">&times;</button>
        </div>

        <div class="mb-4 flex justify-between">
            <input type="text" bind:value={searchTerm} placeholder="Search backups..." class="w-full p-2 border border-gray-300 rounded-md">
            <div class="ml-4">
                <input type="file" bind:this={fileInput} on:change={uploadBackup} accept=".db" class="hidden">
                <button onclick={() => fileInput.click()} class="bg-blue-600 text-white hover:bg-blue-700 font-semibold px-4 py-2 rounded-md">Upload Backup</button>
            </div>
        </div>

        {#if message}
            <p class="mb-4 text-sm {messageStatus === 'success' ? 'text-green-600' : 'text-red-600'}">{message}</p>
        {/if}

        <div class="overflow-auto max-h-96">
            <table class="w-full text-left border-collapse">
                <thead>
                    <tr>
                        <th class="py-2 px-4 border-b">Filename</th>
                        <th class="py-2 px-4 border-b">Size</th>
                        <th class="py-2 px-4 border-b">Date Created</th>
                        <th class="py-2 px-4 border-b">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {#each filteredBackups as backup (backup.filename)}
                        <tr>
                            <td class="py-2 px-4 border-b">{backup.filename}</td>
                            <td class="py-2 px-4 border-b">{formatBytes(backup.size)}</td>
                            <td class="py-2 px-4 border-b">{new Date(backup.created_at).toLocaleString()}</td>
                            <td class="py-2 px-4 border-b">
                                <button onclick={() => downloadBackup(backup.filename)} class="bg-green-600 text-white hover:bg-green-700 font-semibold px-3 py-1 rounded-md mr-2">Download</button>
                                <button onclick={() => restoreBackup(backup.filename)} class="bg-blue-600 text-white hover:bg-blue-700 font-semibold px-3 py-1 rounded-md mr-2">Restore</button>
                                <button onclick={() => deleteBackup(backup.filename)} class="bg-red-600 text-white hover:bg-red-700 font-semibold px-3 py-1 rounded-md">Delete</button>
                            </td>
                        </tr>
                    {/each}
                </tbody>
            </table>
        </div>

        <div class="mt-4 flex justify-end">
            <button onclick={() => showModal = false} class="bg-gray-300 hover:bg-gray-400 text-gray-800 font-semibold px-4 py-2 rounded-md">Close</button>
        </div>
    </div>
</div>
{/if}
