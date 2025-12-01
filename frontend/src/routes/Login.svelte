<script>
  import { token, user } from "../stores/auth";
  import { push } from "svelte-spa-router";

  let username = "";
  let password = "";
  let loading = false;
  let error = "";

  async function handleSubmit(event) {
    event.preventDefault();
    error = "";
    loading = true;

    try {
      const resp = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      if (!resp.ok) {
        const body = await resp.json().catch(() => ({}));
        throw new Error(body.detail || `Login failed (${resp.status})`);
      }

      const data = await resp.json();
      token.set(data.access_token);
      user.set(data.user);

      if (data.user.is_admin) {
        push("/admin");
      } else {
        push("/");
      }
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }
</script>

<form on:submit|preventDefault={handleSubmit}>
  <h2>Admin Login</h2>

  <label>
    Username
    <input type="text" bind:value={username} required />
  </label>

  <label>
    Password
    <input type="password" bind:value={password} required />
  </label>

  {#if error}
    <div class="error">{error}</div>
  {/if}

  <button type="submit" disabled={loading}>
    {#if loading}Logging in...{:else}Login{/if}
  </button>
</form>

<style>
  form {
    max-width: 400px;
    margin: 2rem auto;
    padding: 1.25rem;
    border-radius: 8px;
    box-shadow: 0 1px 6px rgba(0, 0, 0, 0.08);
    text-align: left;
  }

  h2 {
    text-align: center;
    margin-bottom: 1rem;
  }

  label {
    display: block;
    margin-bottom: 0.75rem;
    font-weight: 600;
  }

  input {
    width: 100%;
    padding: 0.5rem;
    margin-top: 0.25rem;
    border: 1px solid #ddd;
    border-radius: 6px;
    box-sizing: border-box;
  }

  .error {
    color: #b00020;
    margin-top: 0.5rem;
    margin-bottom: 0.75rem;
  }

  button {
    width: 100%;
  }
</style>
