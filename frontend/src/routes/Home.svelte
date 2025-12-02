<script>
  import { link } from 'svelte-spa-router';
  import { isAuthenticated, isAdmin } from "../stores/auth";
  import { push } from "svelte-spa-router";

  function handleAdminClick() {
    if ($isAuthenticated && $isAdmin) {
      push("/admin");
    } else {
      push("/login");
    }
  }
</script>

<section class="home">
  <h2>Welcome to the GFS System</h2>
  <p>Select a page to get started:</p>

  <nav>
    <a href="/signup" use:link>Sign Up</a>
    <a href="/match" use:link>Match</a>
    <a href="/ceremony" use:link>Ceremony</a>
    <button type="button" on:click={handleAdminClick}>Admin</button>
  </nav>
</section>

<style>
  .home {
    text-align: center;
    margin-top: 3rem;
  }

  nav {
    display: flex;
    justify-content: center;
    gap: 1.5rem;
    margin-top: 2rem;
  }

  a,
  button {
    padding: 0.75rem 1.25rem;
    background-color: #3b82f6;
    color: white;
    border-radius: 0.5rem;
    text-decoration: none;
    transition: background-color 0.2s;
    border: none;
    cursor: pointer;
    font-size: 1rem;
  }

  a:hover,
  button:hover {
    background-color: #2563eb;
  }
</style>
