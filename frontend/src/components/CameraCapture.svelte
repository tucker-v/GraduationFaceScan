<script>
    import { onMount, onDestroy } from "svelte";
    let videoSource = null;
    let loading = false;
    let stream = null;
    onMount(async () => {
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
</script>

<div>
    {#if loading}
        <h1>LOADING</h1>
    {/if}
    <!-- svelte-ignore a11y-media-has-caption -->
    <video bind:this={videoSource} />
</div>
