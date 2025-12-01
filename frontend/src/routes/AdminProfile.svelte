<script>
  import { authFetch } from "../lib/authFetch";
  import { user, isAdmin } from "../stores/auth";
  import { push } from "svelte-spa-router";

  let oldPassword = "";
  let newPassword = "";
  let confirmPassword = "";
  let success = "";
  let error = "";

  $: if (!$isAdmin) {
    push("/login");
  }
</script>

<section class="profile">
  <h2>Admin Profile</h2>
  <p>Logged in as: {$user?.username}</p>

  <form
    on:submit|preventDefault={async (e) => {
      e.preventDefault();
      success = "";
      error = "";

      if (newPassword !== confirmPassword) {
        error = "New passwords do not match.";
        return;
      }

      try {
        const resp = await authFetch("/api/auth/change-password", {
          method: "POST",
          body: JSON.stringify({
            old_password: oldPassword,
            new_password: newPassword,
          }),
        });

        if (!resp.ok) {
          const body = await resp.json().catch(() => ({}));
          throw new Error(body.detail || `Failed (${resp.status})`);
        }

        success = "Password updated successfully.";
        oldPassword = "";
        newPassword = "";
        confirmPassword = "";
      } catch (err) {
        error = err.message;
      }
    }}
  >
    <h3>Change Password</h3>

    <label>
      Current password
      <input type="password" bind:value={oldPassword} required />
    </label>

    <label>
      New password
      <input type="password" bind:value={newPassword} required />
    </label>

    <label>
      Confirm new password
      <input type="password" bind:value={confirmPassword} required />
    </label>

    {#if error}<div class="error">{error}</div>{/if}
    {#if success}<div class="success">{success}</div>{/if}

    <button type="submit">Update Password</button>
  </form>
</section>

<style>
  .profile {
    max-width: 480px;
    margin: 2rem auto;
    text-align: left;
  }

  h2, h3 {
    text-align: center;
  }

  form {
    margin-top: 1rem;
    padding: 1.25rem;
    border-radius: 8px;
    box-shadow: 0 1px 6px rgba(0, 0, 0, 0.08);
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
  }

  .success {
    color: #16a34a;
    margin-top: 0.5rem;
  }

  button {
    margin-top: 0.75rem;
    width: 100%;
  }
</style>
