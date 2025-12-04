<script>
    import { onMount } from "svelte";

    let loading = false;
    let reports = null;          // full array from API
    let pieReports = [];
    let managerialReports = [];
    let errorMessage = null;

    async function fetchReports() {
        loading = true;
        try {
            const resp = await fetch("/api/reports/charts");
            if (!resp.ok) {
                const body = await resp.json().catch(() => ({}));
                throw new Error(body.detail || `Server returned ${resp.status}`);
            }
            const data = await resp.json();

            // data is an array of 10 images:
            // [5 pie charts..., 5 managerial bar charts...]
            reports = data || [];
            pieReports = reports.slice(0, 5);
            managerialReports = reports.slice(5);
        } catch (err) {
            console.error("Failed to fetch reports:", err);
            errorMessage = `Failed to load reports: ${err.message}`;
        } finally {
            loading = false;
        }
    }

    async function downloadPDF() {
        try {
            const response = await fetch("/api/reports/download", {
                method: "GET",
            });

            if (!response.ok) {
                throw new Error("Failed to download PDF");
            }
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);

            const link = document.createElement("a");
            link.href = url;
            link.download = "charts_report.pdf";
            document.body.appendChild(link);
            link.click();

            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        } catch (err) {
            console.error(err);
            errorMessage = `Failed to download reports: ${err.message}`;
        }
    }

    onMount(() => {
        fetchReports();
    });
</script>

{#if loading}
    <h2>LOADING</h2>
{:else if errorMessage}
    <p class="error">{errorMessage}</p>
{:else}
    <h3>Reports</h3>
    <div class="grid">
        {#each pieReports as img, i}
            <div class="card">
                <img src={img} alt={`report chart ${i + 1}`} />
            </div>
        {/each}
    </div>

    <h3>Managerial Reports</h3>
    <div class="grid">
        {#each managerialReports as img, i}
            <div class="card">
                <img src={img} alt={`managerial report chart ${i + 1}`} />
            </div>
        {/each}
    </div>

    <button on:click={downloadPDF}>Download PDF</button>
{/if}

<style>
    .grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        gap: 1.5rem;
        padding: 1rem;
    }

    .card {
        background: #fafafa;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        text-align: center;
    }

    img {
        width: 100%;
        height: auto;
        margin-top: 0.5rem;
        border-radius: 8px;
    }

    h3 {
        font-size: 1rem;
        margin-bottom: 0.5rem;
        text-transform: capitalize;
    }

    button {
        padding: 0.6rem 1rem;
        background: #0070f3;
        color: white;
        border-radius: 8px;
        border: none;
        cursor: pointer;
        font-size: 1rem;
        margin: 1rem;
    }

    .error {
        color: red;
        padding: 1rem;
    }
</style>
