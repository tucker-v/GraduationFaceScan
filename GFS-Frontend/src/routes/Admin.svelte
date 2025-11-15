<script>
  import { onMount } from 'svelte';

  let students = [];
  let loading = true;
  let error = null;

  async function loadStudents() {
    loading = true;
    error = null;
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
  }

  async function deleteStudent(pid) {
    if (!confirm(`Delete student ${pid}?`)) return;
    try {
      const res = await fetch(`/api/students/${encodeURIComponent(pid)}`, { method: 'DELETE' });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `Delete failed: ${res.status}`);
      }
      // update local list
      students = students.filter(s => String(s.PID) !== String(pid));
    } catch (err) {
      console.error(err);
      error = err.message;
    }
  }

  onMount(loadStudents);
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
          <th>Actions</th>
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
            <td><button class="delete" on:click={() => deleteStudent(s.PID)}>Delete</button></td>
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

  .delete {
    background: #ef4444;
    color: #fff;
    border: none;
    padding: 0.4rem 0.6rem;
    border-radius: 0.25rem;
    cursor: pointer;
  }

  .delete:hover {
    background: #dc2626;
  }
</style>