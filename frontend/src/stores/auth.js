import { writable, derived } from "svelte/store";

const storedToken = typeof localStorage !== "undefined" ? localStorage.getItem("token") : null;
const storedUser = typeof localStorage !== "undefined" ? localStorage.getItem("user") : null;

export const token = writable(storedToken);
export const user = writable(storedUser ? JSON.parse(storedUser) : null);

export const isAuthenticated = derived(token, ($token) => !!$token);
export const isAdmin = derived(user, ($user) => !!$user?.is_admin);

token.subscribe(($token) => {
  if (typeof localStorage === "undefined") return;
  if ($token) localStorage.setItem("token", $token);
  else localStorage.removeItem("token");
});

user.subscribe(($user) => {
  if (typeof localStorage === "undefined") return;
  if ($user) localStorage.setItem("user", JSON.stringify($user));
  else localStorage.removeItem("user");
});
