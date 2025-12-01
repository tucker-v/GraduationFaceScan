<script>
  import { authFetch } from '../lib/authFetch';
  import { token, user, isAuthenticated, isAdmin } from "../stores/auth";
  import { push } from "svelte-spa-router";

  let students = [];
  let ceremonies = [];
  let staff = [];
  let loading = true;
  let error = null;
  let selectedTable = "Students";
  let editingRow = null;
  let editData = {};

  // UI state for Add New Admin modal
  let showAddAdmin = false;
  let newAdminUsername = "";
  let newAdminPassword = "";
  let newAdminMessage = "";
  let newAdminError = "";

  const tables = ["Students", "Staff", "Ceremonies"];

  // Create-form state per table
  let newStudent = {
    PID: "",
    name: "",
    email: "",
    degree_name: "",
    degree_type: "",
    opt_in_biometric: false
  };
  let studentCreateError = "";
  let studentCreateMessage = "";

  let newCeremony = {
    name: "",
    date_time: "",
    location: "",
    start_time: "",
    end_time: ""
  };
  let ceremonyCreateError = "";
  let ceremonyCreateMessage = "";

  let newStaff = {
    staff_id: "",
    name: "",
    email: "",
    status: "active"
  };
  let staffCreateError = "";
  let staffCreateMessage = "";

  // Guard: only authenticated admins can access
  $: if (!$isAuthenticated) {
    push("/login");
  } else if (!$isAdmin) {
    push("/");
  }

  // Load table data when selection changes
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
    students = [];
    staff = [];
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
    students = [];
    staff = [];
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
    staff = [];
    ceremonies = [];
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

  async function deleteCeremony(ceremonyId) {
    if (!confirm(`Delete ceremony ${ceremonyId}?`)) return;
    try {
      const res = await fetch(`/api/ceremonies/${ceremonyId}`, { method: 'DELETE' });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `Delete failed: ${res.status}`);
      }
      ceremonies = ceremonies.filter(c => c.ceremony_id !== ceremonyId);
    } catch (err) {
      console.error(err);
      error = err.message;
    }
  }

  async function deleteStaff(staffId) {
    if (!confirm(`Delete staff ${staffId}?`)) return;
    try {
      const res = await fetch(`/api/staff/${encodeURIComponent(staffId)}`, { method: 'DELETE' });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `Delete failed: ${res.status}`);
      }
      staff = staff.filter(s => s.staff_id !== staffId);
    } catch (err) {
      console.error(err);
      error = err.message;
    }
  }

  async function handleLogout() {
    try {
      await authFetch("/api/auth/logout", { method: "POST" });
    } catch (e) {
      // ignore
    }
    token.set(null);
    user.set(null);
    push("/login");
  }

  function openAddAdmin() {
    showAddAdmin = true;
    newAdminUsername = "";
    newAdminPassword = "";
    newAdminMessage = "";
    newAdminError = "";
  }

  function closeAddAdmin() {
    showAddAdmin = false;
    newAdminUsername = "";
    newAdminPassword = "";
    newAdminMessage = "";
    newAdminError = "";
  }

  async function createAdminUser(event) {
    event.preventDefault();
    newAdminMessage = "";
    newAdminError = "";

    try {
      const res = await authFetch("/api/auth/admin/create", {
        method: "POST",
        body: JSON.stringify({
          username: newAdminUsername,
          password: newAdminPassword
        })
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Failed (${res.status})`);
      }

      const data = await res.json();
      newAdminMessage = `Admin '${data.username}' created.`;
      newAdminUsername = "";
      newAdminPassword = "";
    } catch (err) {
      newAdminError = err.message;
    }
  }

  async function createStudent(e) {
    e.preventDefault();
    studentCreateError = "";
    studentCreateMessage = "";
    try {
      const res = await authFetch("/api/students/", {
        method: "POST",
        body: JSON.stringify(newStudent)
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Failed (${res.status})`);
      }
      const created = await res.json();
      students = [...students, created];
      studentCreateMessage = `Student ${created.PID} added.`;
      newStudent = {
        PID: "",
        name: "",
        email: "",
        degree_name: "",
        degree_type: "",
        opt_in_biometric: false
      };
    } catch (err) {
      studentCreateError = err.message;
    }
  }

  async function createCeremony(e) {
    e.preventDefault();
    ceremonyCreateError = "";
    ceremonyCreateMessage = "";
    try {
      const res = await authFetch("/api/ceremonies/", {
        method: "POST",
        body: JSON.stringify(newCeremony)
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Failed (${res.status})`);
      }
      const created = await res.json();
      ceremonies = [...ceremonies, created];
      ceremonyCreateMessage = `Ceremony ${created.ceremony_id} added.`;
      newCeremony = {
        name: "",
        date_time: "",
        location: "",
        start_time: "",
        end_time: ""
      };
    } catch (err) {
      ceremonyCreateError = err.message;
    }
  }

  async function createStaff(e) {
    e.preventDefault();
    staffCreateError = "";
    staffCreateMessage = "";
    try {
      const res = await authFetch("/api/staff/", {
        method: "POST",
        body: JSON.stringify(newStaff)
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Failed (${res.status})`);
      }
      const created = await res.json();
      staff = [...staff, created];
      staffCreateMessage = `Staff ${created.staff_id} added.`;
      newStaff = {
        staff_id: "",
        name: "",
        email: "",
        status: "active"
      };
    } catch (err) {
      staffCreateError = err.message;
    }
  }
</script>

<section class="admin">
  <div class="row">
    <div class="row-left">
      <h2>Admin Dashboard</h2>
      <button type="button" class="add-admin" on:click={openAddAdmin}>
        Add New Admin
      </button>
    </div>
    <div class="row-right">
      <button type="button" class="profile-btn" on:click={() => push("/admin/profile")}>
        Admin Profile
      </button>
      <button type="button" class="logout-btn" on:click={handleLogout}>
        Logout
      </button>
      <select bind:value={selectedTable}>
        {#each tables as table}
          <option value={table}>{table}</option>
        {/each}
      </select>
    </div>
  </div>

  {#if showAddAdmin}
    <!-- Just to get rid of the warnings-->
    <!-- svelte-ignore a11y_click_events_have_key_events -->
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div class="modal-backdrop" on:click|self={closeAddAdmin}>
      <div class="modal">
        <h3>Add New Admin</h3>
        <form on:submit|preventDefault={createAdminUser}>
          <label>
            Username
            <input type="text" bind:value={newAdminUsername} required />
          </label>
          <label>
            Password
            <input type="password" bind:value={newAdminPassword} required />
          </label>

          {#if newAdminError}
            <div class="error">{newAdminError}</div>
          {/if}
          {#if newAdminMessage}
            <div class="success">{newAdminMessage}</div>
          {/if}

          <div class="modal-actions">
            <button type="submit">Create Admin</button>
            <button type="button" class="cancel" on:click={closeAddAdmin}>Close</button>
          </div>
        </form>
      </div>
    </div>
  {/if}

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
      <div class="create-panel">
        <h3>Add Student</h3>
        <form on:submit|preventDefault={createStudent}>
          <div class="grid">
            <input placeholder="PID" bind:value={newStudent.PID} required />
            <input placeholder="Name" bind:value={newStudent.name} required />
            <input placeholder="Email" type="email" bind:value={newStudent.email} required />
            <input placeholder="Degree" bind:value={newStudent.degree_name} />
            <input placeholder="Type" bind:value={newStudent.degree_type} />
            <label class="checkbox-inline">
              <input type="checkbox" bind:checked={newStudent.opt_in_biometric} />
              Opt-in Biometric
            </label>
          </div>
          {#if studentCreateError}<div class="error">{studentCreateError}</div>{/if}
          {#if studentCreateMessage}<div class="success">{studentCreateMessage}</div>{/if}
          <button type="submit">Add Student</button>
        </form>
      </div>

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
      <div class="create-panel">
        <h3>Add Ceremony</h3>
        <form on:submit|preventDefault={createCeremony}>
          <div class="grid">
            <input placeholder="Name" bind:value={newCeremony.name} required />
            <input
              placeholder="Date & Time (YYYY-MM-DD HH:MM:SS)"
              bind:value={newCeremony.date_time}
              required
            />
            <input placeholder="Location" bind:value={newCeremony.location} required />
            <input placeholder="Start Time (HH:MM:SS)" bind:value={newCeremony.start_time} required />
            <input placeholder="End Time (HH:MM:SS)" bind:value={newCeremony.end_time} required />
          </div>
          {#if ceremonyCreateError}<div class="error">{ceremonyCreateError}</div>{/if}
          {#if ceremonyCreateMessage}<div class="success">{ceremonyCreateMessage}</div>{/if}
          <button type="submit">Add Ceremony</button>
        </form>
      </div>

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
                  <button class="delete" on:click={() => deleteCeremony(c.ceremony_id)}>Delete</button>
                </td>
              </tr>
            {/if}
          {/each}
        </tbody>
      </table>

    {:else if selectedTable === "Staff"}
      <div class="create-panel">
        <h3>Add Staff</h3>
        <form on:submit|preventDefault={createStaff}>
          <div class="grid">
            <input placeholder="Staff ID" bind:value={newStaff.staff_id} required />
            <input placeholder="Name" bind:value={newStaff.name} required />
            <input placeholder="Email" type="email" bind:value={newStaff.email} required />
            <input placeholder="Status" bind:value={newStaff.status} />
          </div>
          {#if staffCreateError}<div class="error">{staffCreateError}</div>{/if}
          {#if staffCreateMessage}<div class="success">{staffCreateMessage}</div>{/if}
          <button type="submit">Add Staff</button>
        </form>
      </div>

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
                  <button class="delete" on:click={() => deleteStaff(s.staff_id)}>Delete</button>
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
    margin-bottom: 0.5rem;
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
  }

  select:hover {
    border-color: #999;
  }

  .row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding: 0.5rem 0 1rem 0;
  }

  .row-left {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .row-right {
    display: flex;
    align-items: center;
    gap: 0.75rem;
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

  .success {
    color: #16a34a;
    text-align: center;
    margin-top: 0.5rem;
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

  .add-admin,
  .profile-btn,
  .logout-btn {
    padding: 0.4rem 0.8rem;
    border-radius: 0.5rem;
    border: none;
    cursor: pointer;
    font-weight: 600;
    color: #fff;
  }

  .add-admin {
    background-color: #3b82f6;
  }

  .add-admin:hover {
    background-color: #2563eb;
  }

  .profile-btn {
    background-color: #3b82f6;
  }

  .profile-btn:hover {
    background-color: #2563eb;
  }

  .logout-btn {
    background-color: #ef4444;
  }

  .logout-btn:hover {
    background-color: #dc2626;
  }

  .create-panel {
    margin-bottom: 1rem;
    padding: 0.75rem 1rem;
    border-radius: 0.5rem;
    background: #111827;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
  }

  .create-panel h3 {
    margin-top: 0;
    margin-bottom: 0.5rem;
  }

  .create-panel .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 0.5rem;
    margin-bottom: 0.5rem;
  }

  .checkbox-inline {
    display: flex;
    align-items: center;
    gap: 0.3rem;
    font-size: 0.9rem;
  }

  /* Modal styles */
  .modal-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(15, 23, 42, 0.7);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 50;
  }

  .modal {
    background: #ffffff;
    color: #111827;
    padding: 1.5rem;
    border-radius: 0.75rem;
    width: 100%;
    max-width: 400px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  }

  .modal h3 {
    margin-top: 0;
    margin-bottom: 1rem;
    text-align: center;
  }

  .modal label {
    display: block;
    margin-bottom: 0.75rem;
    font-weight: 600;
  }

  .modal input {
    width: 100%;
    margin-top: 0.25rem;
  }

  .modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
    margin-top: 1rem;
  }

  .modal-actions button {
    padding: 0.45rem 0.9rem;
    border-radius: 0.5rem;
    border: none;
    cursor: pointer;
    font-weight: 600;
  }

  .modal-actions button:first-child {
    background-color: #3b82f6;
    color: #fff;
  }

  .modal-actions .cancel {
    background-color: #6b7280;
    color: #fff;
  }
</style>
