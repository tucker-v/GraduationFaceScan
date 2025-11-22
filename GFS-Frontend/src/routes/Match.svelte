<script>
    import CameraCapture from "../components/CameraCapture.svelte";

    let capturedImage = null;
    let errorMessage = null;
    let successMessage = null;
    let submitting = null;
    let matchFound = null;

    async function handleSubmit(e) {
        e.preventDefault();

        if (capturedImage == null) {
            return;
        }
        submitting = true;

        try {
            const resp = await fetch("/api/students/match", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    photo: capturedImage,
                }),
            });

            if (!resp.ok) {
                const body = await resp.json().catch(() => ({}));
                throw new Error(
                    body.message || `Server returned ${resp.status}`,
                );
            }

            matchFound = await resp.json();

            successMessage = "Match successful!";
        } catch (err) {
            errorMessage = `Submission failed: ${err.message}`;
        } finally {
            submitting = false;
        }
    }
</script>

<form on:submit|preventDefault={handleSubmit} aria-describedby="form-status">
    {#if !matchFound}
        <h2>Match Face</h2>
        <div style="margin-bottom: 10px;">
            {#if capturedImage}
                <div class="image-container">
                    <h3>Preview:</h3>
                    <img src={capturedImage} alt="Captured frame" />
                    <button
                        on:click={() => {
                            capturedImage = null;
                        }}>Retake</button
                    >
                </div>
            {:else}
                <CameraCapture
                    onCapture={(image) => {
                        capturedImage = image;
                    }}
                />
            {/if}
        </div>

        {#if capturedImage != null}
            <div>
                <button type="submit" disabled={submitting}>
                    {#if submitting}Submitting...{:else}Find Match{/if}
                </button>
            </div>
        {/if}

        <div id="form-status" class="meta" role="status" aria-live="polite">
            {#if successMessage}
                <div class="success">{successMessage}</div>
            {/if}
            {#if errorMessage}
                <div class="server-error">{errorMessage}</div>
            {/if}
        </div>
    {:else}
        <h2>Match Found</h2>
        <div class="match-details">
            <p><strong>PID:</strong> {matchFound.PID}</p>
            <p><strong>Name:</strong> {matchFound.name}</p>
            <p><strong>Email:</strong> {matchFound.email}</p>
            <p><strong>Degree Name:</strong> {matchFound.degree_name}</p>
            <p><strong>Degree Type:</strong> {matchFound.degree_type}</p>
            <p>
                <strong>Biometric Opt-in:</strong>
                {matchFound.opt_in_biometric ? "Yes" : "No"}
            </p>
        </div>

        <div style="margin-top: 1rem;">
            <button
                type="button"
                on:click={() => {
                    capturedImage = null;
                    matchFound = null;
                    successMessage = null;
                    errorMessage = null;
                }}
            >
                Reset
            </button>
        </div>
    {/if}
</form>

<style>
    form {
        max-width: 520px;
        margin: 1rem auto;
        padding: 1.25rem;
        border-radius: 8px;
        box-shadow: 0 1px 6px rgba(0, 0, 0, 0.08);
    }

    .meta {
        margin-top: 0.75rem;
        font-size: 0.95rem;
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

    button[disabled] {
        opacity: 0.6;
        cursor: not-allowed;
    }

    .image-container {
        position: relative;
        width: 100%;
        max-width: 400px; /* optional max width */
        margin: 0 auto; /* center container */
    }

    .image-container img {
        width: 100%;
        height: auto;
        border-radius: 8px;
        display: block;
    }

    .image-container button {
        position: absolute;
        bottom: 10px; /* distance from bottom of video */
        left: 50%; /* start at horizontal center */
        transform: translateX(-50%); /* center the button horizontally */
        padding: 0.5rem 1rem;
        background: #424b56;
        color: white;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        font-size: 1rem;
        opacity: 0.85;
        transition: opacity 0.2s;
    }
    .match-details {
        padding: 1rem;
        border-radius: 6px;
        margin-bottom: 1rem;
    }
</style>
