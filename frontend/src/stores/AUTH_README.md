# Auth & User Management Overview

This document explains how the new authentication and user-account features work, and how frontend engineers can integrate them.

## Data Model

### `USER_ACCOUNT` table

A new PostgreSQL table backs all application logins:

- `user_id` (SERIAL, primary key)
- `username` (VARCHAR, unique, required)
- `password_hash` (VARCHAR, required, bcrypt hash)
- `is_admin` (BOOLEAN, default `FALSE`)
- `created_at` (TIMESTAMP, default `CURRENT_TIMESTAMP`)
- `updated_at` (TIMESTAMP, default `CURRENT_TIMESTAMP`)

### Initial admin seeding

During database setup:

1. The `USER_ACCOUNT` table is created if it does not exist.
2. If `USER_ACCOUNT` is empty, a first admin user is created:

username: admin
password: ChangeMeNow123!

text

This user should log in once and immediately change the password using the **change password** endpoint (see below).

---

## Authentication Model

- Authentication is **stateless JWT**:
  - Clients obtain a JWT via `POST /api/auth/login`.
  - JWT includes `sub` (user_id), `username`, and `is_admin`.
- The token must be sent on protected requests via:

Authorization: Bearer <access_token>

text

- Passwords are **never stored in plain text**; they are hashed using bcrypt.

---

## API Endpoints

All endpoints are under the `/api/auth` prefix.

### 1. `POST /api/auth/signup`

Create a new **non-admin** user.

**Request body**

{
"username": "jdoe",
"password": "some-strong-password"
}

text

**Response 200**

{
"user_id": 2,
"username": "jdoe",
"is_admin": false
}

text

**Error cases**

- `409 Conflict` – `username` already exists.

**Notes for frontend**

- Use this to register standard users (not admins).
- After signup, you can automatically redirect to the login page or auto-log them in by calling `/login`.

---

### 2. `POST /api/auth/login`

Authenticate a user and obtain a JWT.

**Request body**

{
"username": "admin",
"password": "ChangeMeNow123!"
}

text

**Response 200**

{
"access_token": "<JWT_TOKEN_STRING>",
"token_type": "bearer",
"user": {
"user_id": 1,
"username": "admin",
"is_admin": true
}
}

text

**Error cases**

- `401 Unauthorized` – invalid username or password.

**Frontend integration**

- On success:
  - Store `access_token` (e.g., `localStorage`, or a Svelte store).
  - Store basic user info (`user_id`, `username`, `is_admin`).
- For any subsequent authenticated request:

const token = getTokenSomehow();

fetch("/some/protected/endpoint", {
method: "GET",
headers: {
"Authorization": Bearer ${token},
"Content-Type": "application/json"
}
});

text

---

### 3. `POST /api/auth/change-password`

Allow a **logged-in** user to change their password.

**Headers**

Authorization: Bearer <access_token>
Content-Type: application/json

text

**Request body**

{
"old_password": "old-password",
"new_password": "new-strong-password"
}

text

**Response 200**

{ "status": "ok" }

text

**Error cases**

- `401 Unauthorized` – token missing/invalid OR `old_password` does not match the stored hash.

**Frontend integration**

- Provide a “Change Password” form for logged-in users.
- After success, consider:
  - Logging the user out (clear token) and forcing re-login, **or**
  - Keeping them logged in but informing them the password changed successfully.

---

### 4. `POST /api/auth/admin/create`

Create a **new admin user** – only available to users who are already admins.

**Headers**

Authorization: Bearer <access_token> # token for an admin user (is_admin === true)
Content-Type: application/json

text

**Request body**

{
"username": "newadmin",
"password": "some-strong-password"
}

text

**Response 200**

{
"user_id": 3,
"username": "newadmin",
"is_admin": true
}

text

**Error cases**

- `403 Forbidden` – current user is **not** an admin.
- `401 Unauthorized` – missing/invalid/expired token.
- `409 Conflict` – `username` already exists.

**Frontend integration**

- In the Admin UI, show an “Add Admin” form only when `currentUser.is_admin === true`.
- On submit, call this endpoint with the stored token.
- On success, update any admin list or show a success message.

---

### 5. `POST /api/auth/logout`

Logically logs the user out. The app is stateless, so true logout is “forget the token on the client”.

**Headers**

Authorization: Bearer <access_token>

text

**Request body**

- None.

**Response 200**

{ "status": "logged_out" }

text

**Frontend integration**

- Main action is on the client:
  - Remove token from storage (e.g., `localStorage.removeItem("token")`).
  - Clear any in-memory auth stores.
  - Redirect to login or home.
- Calling this endpoint is optional but can be used for consistent API usage or analytics.

---

## Frontend Implementation Guide

### Global auth handling

- Maintain an auth store (e.g., Svelte store) containing:
  - `token` (JWT)
  - `user` (`user_id`, `username`, `is_admin`)
  - `isAuthenticated` derived from whether `token` is present/valid
- On app start:
  - Read token from persistent storage.
  - Optionally decode/inspect expiration or ping a trivial protected endpoint to validate.

### Example Svelte flow

**Login page**

1. Collect `username` and `password`.
2. `POST /api/auth/login`.
3. On success:
   - Save `access_token` and `user`.
   - Navigate to `/admin` if `is_admin === true`, or to a regular user dashboard otherwise.

**Protected routes**

- Wrap fetch calls in a helper:

async function authFetch(url, options = {}) {
const token = getTokenFromStore();
const headers = {
...(options.headers || {}),
"Content-Type": "application/json",
...(token ? { "Authorization": Bearer ${token} } : {})
};

const resp = await fetch(url, { ...options, headers });
if (resp.status === 401 || resp.status === 403) {
// handle auth failure: clear state, redirect to login, etc.
}
return resp;
}

text

**Admin-only UI**

- Conditionally render admin features (like “Create Admin” form, admin dashboard sections) only when `user.is_admin` is `true`.

{#if $auth.user?.is_admin}

<!-- Admin-only components -->
{/if}

text

**Change password**

- Use a simple form bound to `/api/auth/change-password` through `authFetch`.
- On success, optionally:
  - Call `/api/auth/logout`.
  - Clear token + state and route back to login.

---

## Summary of Endpoints

| Endpoint                   | Method | Auth Required           | Purpose                         |
|---------------------------|--------|-------------------------|---------------------------------|
| `/api/auth/signup`        | POST   | No                      | Create regular (non-admin) user |
| `/api/auth/login`         | POST   | No                      | Obtain JWT + user info          |
| `/api/auth/change-password` | POST | Yes (any logged-in user)| Change own password             |
| `/api/auth/admin/create`  | POST   | Yes (admin only)        | Create a new admin user         |
| `/api/auth/logout`        | POST   | Yes                     | Logical logout (client discards token) |