<script>
    import { onMount, onDestroy } from "svelte";

    export let onCapture;
    let videoSource = null;
    let loading = false;
    let stream = null;

    async function startCamera() {
        try {
            loading = true;
            stream = await navigator.mediaDevices.getUserMedia({
                video: true,
            });
            videoSource.srcObject = stream;
            videoSource.play();
            loading = false;
        } catch (error) {
            console.log(error);
        }
    }
    onMount(() => {
        startCamera();
    });

    onDestroy(() => {
        // stop all camera tracks
        if (stream) {
            stream.getTracks().forEach((track) => track.stop());
            stream = null;
        }
        if (videoSource) {
            videoSource.srcObject = null; // clear ref for good measure
        }
    });

    function capture() {
        if (!videoSource) return;

        const canvas = document.createElement("canvas");
        canvas.width = videoSource.videoWidth;
        canvas.height = videoSource.videoHeight;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(videoSource, 0, 0, canvas.width, canvas.height);

        const capturedImage = canvas.toDataURL("image/png");
        onCapture(capturedImage)
    }
</script>

<div>
    {#if loading}
        <h1>LOADING</h1>
    {/if}

    <div class="camera-container">
        <!-- svelte-ignore a11y-media-has-caption -->
        <video bind:this={videoSource} />

        <button on:click={capture}>Capture Image</button>
    </div>
</div>


<style>
   .camera-container {
    position: relative;
    width: 100%;
    max-width: 400px; /* optional max width */
    margin: 0 auto;    /* center container */
  }

  .camera-container video {
    width: 100%;
    height: auto;
    border-radius: 8px;
    display: block;
  }

  .camera-container button {
    position: absolute;
    bottom: 10px;         /* distance from bottom of video */
    left: 50%;            /* start at horizontal center */
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

  .camera-container button:hover {
    opacity: 1;
  }
</style>
