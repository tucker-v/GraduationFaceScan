<script>

    import {onMount} from 'svelte'

    export let ceremonyId;
    let called = null;
    let pending = null;
    let loading = false;
    let errorMessage = null;

    async function fetchQueue() {
        loading = true;
        try {
            const resp = await fetch("/api/queue/view", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    ceremony_id: ceremonyId
                }),
            });
            if (!resp.ok) {
                const body = await resp.json().catch(() => ({}));
                throw new Error(
                    body.detail || `Server returned ${resp.status}`,
                );
            }
            const result = await resp.json();

            pending = result.pending
            called = result.called

        } catch (err) {
            console.error("Failed to fetch queue:", err);
            errorMessage = `Failed to load queue: ${err.message}`;
        } finally {
            loading = false;
        }
    }
    onMount(()=> {
        fetchQueue();
    })
</script>

{#if loading}
    <p>Loading queue...</p>
{:else if errorMessage}
    <p class="error">{errorMessage}</p>
{:else}
    <div class="tables">
        <!-- Pending Table -->
        <div>
            <h2>Pending</h2>
            {#if pending && pending.length > 0}
                <table>
                    <thead>
                        <tr>
                            <th>PID</th>
                            <th>Name</th>
                            <th>Degree</th>
                            <th>Type</th>
                            <th>Queued At</th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each pending as p}
                            <tr>
                                <td>{p.PID}</td>
                                <td>{p.name}</td>
                                <td>{p.degree_name}</td>
                                <td>{p.degree_type}</td>
                                <td>{new Date(p.time_queued).toLocaleString()}</td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            {:else}
                <p>No pending students.</p>
            {/if}
        </div>

        <!-- Called Table -->
        <div>
            <h2>Called</h2>
            {#if called && called.length > 0}
                <table>
                    <thead>
                        <tr>
                            <th>PID</th>
                            <th>Name</th>
                            <th>Degree</th>
                            <th>Type</th>
                            <th>Queued At</th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each called as c}
                            <tr>
                                <td>{c.PID}</td>
                                <td>{c.name}</td>
                                <td>{c.degree_name}</td>
                                <td>{c.degree_type}</td>
                                <td>{new Date(c.time_queued).toLocaleString()}</td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            {:else}
                <p>No called students.</p>
            {/if}
        </div>
    </div>
{/if}

<style>
    .tables {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2rem;
        margin-top: 1rem;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 0.5rem;
    }

    th, td {
        border: 1px solid #ccc;
        padding: 8px;
        font-size: 0.9rem;
    }

    h2 {
        margin-bottom: 0.25rem;
    }

    .error {
        color: red;
        font-weight: bold;
    }
</style>
