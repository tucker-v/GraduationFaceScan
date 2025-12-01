import { get } from "svelte/store";
import { token } from "../stores/auth";

export async function authFetch(input, init = {}) {
  const t = get(token);
  const headers = {
    "Content-Type": "application/json",
    ...(init.headers || {}),
    ...(t ? { Authorization: `Bearer ${t}` } : {}),
  };

  const resp = await fetch(input, { ...init, headers });

  // Optionally handle 401/403 centrally (clear auth, redirect, etc.)
  return resp;
}
