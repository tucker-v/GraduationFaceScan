<script>
    import CameraCapture from "../components/CameraCapture.svelte";
    import { onMount } from 'svelte';
    // form state
    let pid = "";
    let name = "";
    let email = "";
    let degree = "";
    let type = "";
    let optedIn = false;
    let capturedImage = null;
    let degrees = null;

    // UI state
    let submitting = false;
    let successMessage = "";
    let errorMessage = "";
    let errors = {};

    const types = ["BS", "MS", "PHD"];

    async function getDegrees() {
        try {
            const resp = await fetch("/api/degrees/");
            if (!resp.ok) {
                const body = await resp.json().catch(() => ({}));
                throw new Error(
                    body.detail || `Server returned ${resp.status}`,
                );
            }
            degrees = await resp.json();
        } catch (err) {
            console.error("Failed to fetch degrees:", err);
            errorMessage = `Failed to load degrees: ${err.message}`;
            degrees = [];
        }
    }

    onMount(getDegrees);

    function validate() {
        errors = {};
        if (!pid.trim()) errors.pid = "PID is required.";
        if (!name.trim()) errors.name = "Name is required.";
        if (!email.trim()) {
            errors.email = "Email is required.";
        } else {
            // simple email check
            const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!re.test(email))
                errors.email = "Please enter a valid email address.";
        }
        if (!degree) errors.degree = "Please select a degree.";
        if (!type) errors.type = "Please select a type.";
        if (optedIn && !capturedImage) errors.photo = "Please take a photo";
        return Object.keys(errors).length === 0;
    }

    async function handleSubmit(e) {
        e.preventDefault();
        successMessage = "";
        errorMessage = "";

        if (!validate()) {
            return;
        }

        submitting = true;
        try {
            // Example POST - change URL to your backend route
            const resp = await fetch("/api/students/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    PID: pid.trim(),
                    name: name.trim(),
                    email: email.trim(),
                    degree_name: degree,
                    degree_type: type,
                    opt_in_biometric: optedIn,
                    photo: capturedImage,
                }),
            });

            if (!resp.ok) {
                const body = await resp.json().catch(() => ({}));
                throw new Error(
                    body.message || `Server returned ${resp.status}`,
                );
            }

            successMessage = "Signup successful — thank you!";
            // reset form if desired
            pid = "";
            name = "";
            email = "";
            degree = "";
            type = "";
            optedIn = false;
            capturedImage = null;
        } catch (err) {
            errorMessage = `Submission failed: ${err.message}`;
        } finally {
            submitting = false;
            // clear errors after success
            if (successMessage) errors = {};
        }
    }
</script>

<form on:submit|preventDefault={handleSubmit} aria-describedby="form-status">
    <h2>Sign up</h2>

    <div>
        <label for="pid">PID</label>
        <input
            id="pid"
            type="text"
            bind:value={pid}
            aria-invalid={errors.pid ? "true" : "false"}
        />
        {#if errors.pid}<div class="error">{errors.pid}</div>{/if}
    </div>

    <div>
        <label for="name">Name</label>
        <input
            id="name"
            type="text"
            bind:value={name}
            aria-invalid={errors.name ? "true" : "false"}
        />
        {#if errors.name}<div class="error">{errors.name}</div>{/if}
    </div>

    <div>
        <label for="email">Email</label>
        <input
            id="email"
            type="email"
            bind:value={email}
            aria-invalid={errors.email ? "true" : "false"}
        />
        {#if errors.email}<div class="error">{errors.email}</div>{/if}
    </div>

    <div class="row">
        <div>
            <label for="degree">Degree</label>
            <select
                id="degree"
                bind:value={degree}
                aria-invalid={errors.degree ? "true" : "false"}
            >
                <option value="" disabled selected>— select degree —</option>
                {#each degrees as d}
                    <option value={d}>{d}</option>
                {/each}
            </select>
            {#if errors.degree}<div class="error">{errors.degree}</div>{/if}
        </div>

        <div>
            <label for="type">Type</label>
            <select
                id="type"
                bind:value={type}
                aria-invalid={errors.type ? "true" : "false"}
            >
                <option value="" disabled selected>— select type —</option>
                {#each types as t}
                    <option value={t}>{t}</option>
                {/each}
            </select>
            {#if errors.type}<div class="error">{errors.type}</div>{/if}
        </div>
    </div>

    <div class="checkbox">
        <input id="optedIn" type="checkbox" bind:checked={optedIn} />
        <label for="optedIn">Opted In (Biometric)</label>
    </div>
    {#if optedIn}
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
            {#if errors.photo}<div class="error">{errors.photo}</div>{/if}
        </div>
    {/if}

    <div>
        <button type="submit" disabled={submitting}>
            {#if submitting}Submitting...{:else}Sign up{/if}
        </button>
    </div>

    <div id="form-status" class="meta" role="status" aria-live="polite">
        {#if successMessage}
            <div class="success">{successMessage}</div>
        {/if}
        {#if errorMessage}
            <div class="server-error">{errorMessage}</div>
        {/if}
    </div>
</form>

<style>
    form {
        max-width: 520px;
        margin: 1rem auto;
        padding: 1.25rem;
        border-radius: 8px;
        box-shadow: 0 1px 6px rgba(0, 0, 0, 0.08);
    }

    label {
        display: block;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }

    input[type="text"],
    input[type="email"],
    select {
        width: 100%;
        padding: 0.5rem;
        border: 1px solid #ddd;
        border-radius: 6px;
        margin-bottom: 0.5rem;
        box-sizing: border-box;
    }

    .row {
        display: flex;
        gap: 0.75rem;
    }

    .row > div {
        flex: 1;
    }

    .checkbox {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin: 0.5rem 0 1rem 0;
    }

    .error {
        color: #b00020;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
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
</style>
