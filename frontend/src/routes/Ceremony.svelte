<script>
    import { onMount } from "svelte";
    import QueueView from "../components/QueueView.svelte"

    let ceremonies = [];
    let selectedCeremony = null;
    let errorMessage = null;
    let loading = false;
    let started = false;
    let currentStudent = null;
    let loadingStudent = false;
    let queueEmpty = false;
    let showQueue = false;

    async function fetchCeremonies() {
        loading = true;
        try {
            const resp = await fetch("/api/ceremonies/");
            if (!resp.ok) {
                const body = await resp.json().catch(() => ({}));
                throw new Error(
                    body.detail || `Server returned ${resp.status}`,
                );
            }
            ceremonies = await resp.json();
            if (ceremonies.length > 0) {
                selectedCeremony = ceremonies[0]; // default to first ceremony
            }
        } catch (err) {
            console.error("Failed to fetch ceremonies:", err);
            errorMessage = `Failed to load ceremonies: ${err.message}`;
        } finally {
            loading = false;
        }
    }
    async function getNextStudent() {
        if (!selectedCeremony) {
            errorMessage = "Please select a ceremony first.";
            return;
        }

        queueEmpty = false;
        loadingStudent = true;
        errorMessage = null;

        try {
            const resp = await fetch("/api/queue/pop", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ ceremony_id: selectedCeremony.ceremony_id })
            });

            if (!resp.ok) {
                const body = await resp.json().catch(() => ({}));
                throw new Error(body.detail || `Server returned ${resp.status}`);
            }

            const student = await resp.json();

            currentStudent = student;

        } catch (err) {
            console.error("Failed to pop next student:", err);

            if (err.message === "No pending students in queue") {
                queueEmpty = true;
            } else {
                errorMessage = `Error: ${err.message}`;
            }
            currentStudent = null;
        } finally {
            loadingStudent = false;
        }
    }

    onMount(() => {
        fetchCeremonies();
    });
</script>

{#if loading}
    <p>Loading ceremonies...</p>
{:else if errorMessage}
    <p class="error">{errorMessage}</p>
{:else if !started}
    <label for="ceremony-select">Select Ceremony:</label>
    <select id="ceremony-select" bind:value={selectedCeremony}>
        {#each ceremonies as ceremony}
            <option value={ceremony}>
                {ceremony.name} ({ceremony.date_time})
            </option>
        {/each}
    </select>
    <button
        type="button"
        on:click={() => {
            started = true;
        }}
    >
        Start
    </button>
{:else}
    <div class="queue-container">
        <div class="header-row">
            <h1>{selectedCeremony.name}</h1>

            <label class="switch">
                <input type="checkbox" bind:checked={showQueue}>
                <span class="slider"></span>
            </label>
        </div>

        {#if showQueue}
            <QueueView ceremonyId={selectedCeremony.ceremony_id}/>
        {:else}
            {#if currentStudent}
                <div class="match-details">
                    <p><strong>PID:</strong> {currentStudent.PID}</p>
                    <p><strong>Name:</strong> {currentStudent.name}</p>
                    <p><strong>Degree Name:</strong> {currentStudent.degree_name}</p>
                    <p><strong>Degree Type:</strong> {currentStudent.degree_type}</p>
                </div>
            {:else if queueEmpty}
                <p class="label">No students currently in the queue</p>
            {/if}
                <button
                type="button"
                on:click={() => {
                    getNextStudent();
                }}
                >
                    Next
                </button>
        {/if}
    </div>
{/if}

<style>
    label {
        font-weight: bold;
        margin-right: 0.5rem;
    }
    select {
        padding: 0.4rem 0.6rem;
        border-radius: 4px;
        border: 1px solid #ccc;
    }
    .error {
        color: red;
        font-weight: bold;
    }
    button {
        background: #2563eb;
        color: white;
        border: none;
        padding: 0.6rem 1rem;
        border-radius: 6px;
        cursor: pointer;
        font-weight: 600;
        width: 30%;
        margin: 0 auto; /* Center it */
    }
    .match-details {
        padding: 1rem;
        border-radius: 6px;
        margin-bottom: 1rem;
    }
    .header-row {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .switch {
        position: relative;
        display: inline-block;
        width: 48px;
        height: 24px;
    }

    .switch input {
        opacity: 0;
        width: 0;
        height: 0;
    }

    .slider {
        position: absolute;
        cursor: pointer;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: #ccc;
        border-radius: 24px;
        transition: 0.3s;
    }

    .slider:before {
        position: absolute;
        content: "";
        height: 18px;
        width: 18px;
        left: 3px;
        bottom: 3px;
        background-color: white;
        border-radius: 50%;
        transition: 0.3s;
    }

    input:checked + .slider {
        background-color: #4caf50;
    }

    input:checked + .slider:before {
        transform: translateX(24px);
    }
    .queue-container {
        max-width: 900px;
        margin: 0 auto;
        padding: 1.5rem;
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
        justify-content: center;
    }
</style>
