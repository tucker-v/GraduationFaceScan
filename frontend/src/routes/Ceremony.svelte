<script>
    import { onMount } from "svelte";

    let ceremonies = [];
    let selectedCeremony = null;
    let errorMessage = null;
    let loading = false;
    let started = false;
    let currentStudent = null;
    let loadingStudent = false;
    let queueEmpty = false;

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
    <h1>{selectedCeremony.name}</h1>

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
    }
    .match-details {
        padding: 1rem;
        border-radius: 6px;
        margin-bottom: 1rem;
    }
</style>
