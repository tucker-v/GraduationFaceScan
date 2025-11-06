<script>
  import { onMount } from 'svelte';

  let students = $state([]);
  let loading = $state(true);
  let error = $state(null);

  onMount(async () => {
    try {
      const res = await fetch('/api/students/');
      if (!res.ok) {
        throw new Error(`Failed to fetch students: ${res.status}`);
      }
      students = await res.json();
    } catch (err) {
      console.error(err);
      error = err.message;
    } finally {
      loading = false;
    }
  });
</script>

<section class="admin">
  <h2>Admin Dashboard</h2>

  {#if loading}
    <p>Loading students...</p>

  {:else if error}
    <p class="error">Error: {error}</p>

  {:else if students.length === 0}
    <p>No students found.</p>

  {:else}
    <table>
      <thead>
        <tr>
          <th>PID</th>
          <th>Name</th>
          <th>Email</th>
          <th>Degree</th>
          <th>Type</th>
          <th>Opted In (Biometric)</th>
        </tr>
      </thead>
      <tbody>
        {#each students as s}
          <tr>
            <td>{s.PID}</td>
            <td>{s.name}</td>
            <td>{s.email}</td>
            <td>{s.degree_name}</td>
            <td>{s.degree_type}</td>
            <td>{s.opt_in_biometric ? 'Yes' : 'No'}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}
</section>

<style>
  .admin {
    max-width: 900px;
    margin: 2rem auto;
    padding: 1rem;
  }

  h2 {
    text-align: center;
    margin-bottom: 1rem;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    background-color: #000000;
    border-radius: 0.5rem;
    overflow: hidden;
  }

  th, td {
    padding: 0.75rem;
    border-bottom: 1px solid #e5e7eb;
    text-align: left;
  }

  th {
    background-color: #3b82f6;
    color: white;
  }

  tr:hover {
    background-color: #e0e7ff;
  }

  .error {
    color: #dc2626;
    text-align: center;
  }
</style>