<script>
  import { onMount } from 'svelte';

  let students = [];
  let ceremonies = [];
  let staff = []
  let loading = true;
  let error = null;
  let selectedTable = "Students"
  let editingRow = null;
  let editData = {};
  
  const tables = ["Students", "Staff", "Ceremonies"]

  $: switch (selectedTable) {
    case "Students":
      loadStudents();
      break;
    case "Ceremonies":
      loadCeremonies();
      break;
    case "Staff":
      loadStaff();
      break;
  }


  async function loadCeremonies() {
    students = []
    staff = []
    loading = true;
    error = null;
    try {
      const res = await fetch('/api/ceremonies/');
      if (!res.ok) {
        throw new Error(`Failed to fetch ceremonies: ${res.status}`);
      }
      ceremonies = await res.json();
    } catch (err) {
      console.error(err);
      error = err.message;
    } finally {
      loading = false;
    }
  }

  async function loadStaff() {
    students = []
    staff = []
    loading = true;
    error = null;
    try {
      const res = await fetch('/api/staff/');
      if (!res.ok) {
        throw new Error(`Failed to fetch staff: ${res.status}`);
      }
      staff = await res.json();
    } catch (err) {
      console.error(err);
      error = err.message;
    } finally {
      loading = false;
    }
  }

  async function loadStudents() {
    staff = []
    ceremonies = []
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

  function startEditStudent(student) {
    editingRow = `student-${student.PID}`;
    editData = { ...student };
  }

  function cancelEdit() {
    editingRow = null;
    editData = {};
  }

  async function saveStudent() {
    try {
      const res = await fetch(`/api/students/${encodeURIComponent(editData.PID)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editData)
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `Update failed: ${res.status}`);
      }
      const updated = await res.json();
      students = students.map(s => String(s.PID) === String(editData.PID) ? updated : s);
      editingRow = null;
      editData = {};
    } catch (err) {
      console.error(err);
      error = err.message;
    }
  }

  function startEditStaff(staffMember) {
    editingRow = `staff-${staffMember.staff_id}`;
    editData = { ...staffMember };
  }

  async function saveStaff() {
    try {
      const res = await fetch(`/api/staff/${encodeURIComponent(editData.staff_id)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editData)
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `Update failed: ${res.status}`);
      }
      const updated = await res.json();
      staff = staff.map(s => s.staff_id === editData.staff_id ? updated : s);
      editingRow = null;
      editData = {};
    } catch (err) {
      console.error(err);
      error = err.message;
    }
  }

  function startEditCeremony(ceremony) {
    editingRow = `ceremony-${ceremony.ceremony_id}`;
    editData = { ...ceremony };
  }

  async function saveCeremony() {
    try {
      const res = await fetch(`/api/ceremonies/${editData.ceremony_id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editData)
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `Update failed: ${res.status}`);
      }
      const updated = await res.json();
      ceremonies = ceremonies.map(c => c.ceremony_id === editData.ceremony_id ? updated : c);
      editingRow = null;
      editData = {};
    } catch (err) {
      console.error(err);
      error = err.message;
    }
  }

</script>

<section class="admin">
  <div class="row">
    <h2>Admin Dashboard</h2>
    <select bind:value={selectedTable}>
        {#each tables as table}
          <option value={table}>{table}</option>
        {/each}
    </select>
  </div>

  {#if loading}
    <p>Loading {selectedTable}...</p>

  {:else if error}
    <p class="error">Error: {error}</p>

  {:else if (selectedTable === "Students" && students.length === 0)
         || (selectedTable === "Ceremonies" && ceremonies.length === 0)
         || (selectedTable === "Staff" && staff.length === 0)
  }
    <p>No {selectedTable} found.</p>

  {:else}

    {#if selectedTable === "Students"}
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
            {#if editingRow === `student-${s.PID}`}
              <tr class="editing">
                <td>{s.PID}</td>
                <td><input type="text" bind:value={editData.name} /></td>
                <td><input type="email" bind:value={editData.email} /></td>
                <td><input type="text" bind:value={editData.degree_name} /></td>
                <td><input type="text" bind:value={editData.degree_type} /></td>
                <td><input type="checkbox" bind:checked={editData.opt_in_biometric} /></td>
                <td>
                  <button class="save" on:click={saveStudent}>Save</button>
                  <button class="cancel" on:click={cancelEdit}>Cancel</button>
                </td>
              </tr>
            {:else}
              <tr>
                <td>{s.PID}</td>
                <td>{s.name}</td>
                <td>{s.email}</td>
                <td>{s.degree_name}</td>
                <td>{s.degree_type}</td>
                <td>{s.opt_in_biometric ? 'Yes' : 'No'}</td>
                <td>
                  <button class="edit" on:click={() => startEditStudent(s)}>Edit</button>
                  <button class="delete" on:click={() => deleteStudent(s.PID)}>Delete</button>
                </td>
              </tr>
            {/if}
          {/each}
        </tbody>
      </table>

    {:else if selectedTable === "Ceremonies"}
      <table>
        <thead>
          <tr>
            <th>Ceremony ID</th>
            <th>Name</th>
            <th>Date</th>
            <th>Location</th>
            <th>Start Time</th>
            <th>End Time</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {#each ceremonies as c}
            {#if editingRow === `ceremony-${c.ceremony_id}`}
              <tr class="editing">
                <td>{c.ceremony_id}</td>
                <td><input type="text" bind:value={editData.name} /></td>
                <td><input type="datetime-local" bind:value={editData.date_time} /></td>
                <td><input type="text" bind:value={editData.location} /></td>
                <td><input type="time" bind:value={editData.start_time} /></td>
                <td><input type="time" bind:value={editData.end_time} /></td>
                <td>
                  <button class="save" on:click={saveCeremony}>Save</button>
                  <button class="cancel" on:click={cancelEdit}>Cancel</button>
                </td>
              </tr>
            {:else}
              <tr>
                <td>{c.ceremony_id}</td>
                <td>{c.name}</td>
                <td>{c.date_time}</td>
                <td>{c.location}</td>
                <td>{c.start_time}</td>
                <td>{c.end_time}</td>
                <td>
                  <button class="edit" on:click={() => startEditCeremony(c)}>Edit</button>
                </td>
              </tr>
            {/if}
          {/each}
        </tbody>
      </table>

    {:else if selectedTable === "Staff"}
        <table>
        <thead>
          <tr>
            <th>Staff ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {#each staff as s}
            {#if editingRow === `staff-${s.staff_id}`}
              <tr class="editing">
                <td>{s.staff_id}</td>
                <td><input type="text" bind:value={editData.name} /></td>
                <td><input type="email" bind:value={editData.email} /></td>
                <td><input type="text" bind:value={editData.status} /></td>
                <td>
                  <button class="save" on:click={saveStaff}>Save</button>
                  <button class="cancel" on:click={cancelEdit}>Cancel</button>
                </td>
              </tr>
            {:else}
              <tr>
                <td>{s.staff_id}</td>
                <td>{s.name}</td>
                <td>{s.email}</td>
                <td>{s.status}</td>
                <td>
                  <button class="edit" on:click={() => startEditStaff(s)}>Edit</button>
                </td>
              </tr>
            {/if}
          {/each}
        </tbody>
      </table>




    {/if}

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

  select {
    padding: 0.5rem 0.75rem;
    font-size: 1rem;
    border: 1px solid #ccc;
    border-radius: 6px;
    outline: none;
    cursor: pointer;
    transition: border-color 0.2s ease;
    margin-bottom: 0.5rem;
  }

  select:hover {
    border-color: #999;
  }

  .row {
    display: flex;
    align-items: center;     
    justify-content: space-between; 
    gap: 1rem;              
    padding: 0.5rem 0;
  }

  .row h2 {
    margin: 0;              
  }

  th {
    background-color: #3b82f6;
    color: white;
  }

  tr:hover {
    background-color: #e0e7ff56;
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

  .edit {
    background: #3b82f6;
    color: #fff;
    border: none;
    padding: 0.4rem 0.6rem;
    border-radius: 0.25rem;
    cursor: pointer;
    margin-right: 0.3rem;
  }

  .edit:hover {
    background: #2563eb;
  }

  .save {
    background: #10b981;
    color: #fff;
    border: none;
    padding: 0.4rem 0.6rem;
    border-radius: 0.25rem;
    cursor: pointer;
    margin-right: 0.3rem;
  }

  .save:hover {
    background: #059669;
  }

  .cancel {
    background: #6b7280;
    color: #fff;
    border: none;
    padding: 0.4rem 0.6rem;
    border-radius: 0.25rem;
    cursor: pointer;
  }

  .cancel:hover {
    background: #4b5563;
  }

  .editing {
    background-color: #fef3c7 !important;
  }

  input {
    width: 100%;
    padding: 0.25rem 0.5rem;
    border: 1px solid #ccc;
    border-radius: 0.25rem;
    font-size: 0.875rem;
  }

  input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
  }

  input[type="checkbox"] {
    width: auto;
    cursor: pointer;
  }
</style>