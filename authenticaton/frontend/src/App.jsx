import { useEffect, useState } from "react";

const API = "http://localhost:8000";

export default function App() {
  const [mode, setMode] = useState("login"); // "login" or "register"
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [message, setMessage] = useState(null); // { type: "success" | "error", text }
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState(null); // set when logged in
  const [checking, setChecking] = useState(!!localStorage.getItem("token"));

  // On page load: if a token is saved, ask the server who we are
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) return;
    fetch(`${API}/me`, { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => (res.ok ? res.json() : Promise.reject()))
      .then(setUser)
      .catch(() => localStorage.removeItem("token")) // expired or invalid
      .finally(() => setChecking(false));
  }, []);

  const change = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  // FastAPI errors come as {detail: "text"} or, for bad input, {detail: [{msg}]}
  const errorText = (data) =>
    typeof data.detail === "string"
      ? data.detail
      : data.detail?.[0]?.msg ?? "Something went wrong";

  const switchMode = (next) => {
    setMode(next);
    setMessage(null);
  };

  const submit = async (e) => {
    e.preventDefault();
    setMessage(null);
    setLoading(true);
    try {
      if (mode === "register") {
        const res = await fetch(`${API}/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(form),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(errorText(data));
        setMode("login");
        setForm({ name: "", email: form.email, password: "" });
        setMessage({ type: "success", text: data.message });
      } else {
        // 1. log in and get the token
        const res = await fetch(`${API}/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: form.email, password: form.password }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(errorText(data));
        localStorage.setItem("token", data.access_token);

        // 2. use the token to load the user's details
        const meRes = await fetch(`${API}/me`, {
          headers: { Authorization: `Bearer ${data.access_token}` },
        });
        setUser(await meRes.json());
        setForm({ name: "", email: "", password: "" });
      }
    } catch (err) {
      const offline = err instanceof TypeError; // fetch fails if the server is down
      setMessage({
        type: "error",
        text: offline ? "Cannot reach the server. Is the backend running?" : err.message,
      });
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
    setMessage({ type: "success", text: "You have been logged out." });
  };

  if (checking) {
    return <Page><p className="text-center text-gray-500">Loading...</p></Page>;
  }

  // ---------- Dashboard (after login) ----------
  if (user) {
    return (
      <Page>
        <h1 className="text-2xl font-bold text-gray-800">Welcome, {user.name}! 👋</h1>
        <p className="mt-2 text-gray-600">You are logged in as {user.email}</p>
        <button
          onClick={logout}
          className="mt-6 w-full rounded-lg bg-red-500 py-2 font-semibold text-white hover:bg-red-600"
        >
          Logout
        </button>
      </Page>
    );
  }

  // ---------- Login / Register form ----------
  const input = "w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none";

  return (
    <Page>
      <div className="mb-6 flex rounded-lg bg-gray-100 p-1">
        {["login", "register"].map((m) => (
          <button
            key={m}
            type="button"
            onClick={() => switchMode(m)}
            className={`flex-1 rounded-md py-2 font-semibold capitalize ${
              mode === m ? "bg-white text-indigo-600 shadow" : "text-gray-500"
            }`}
          >
            {m}
          </button>
        ))}
      </div>

      {message && (
        <p
          className={`mb-4 rounded-lg px-3 py-2 text-sm ${
            message.type === "success" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
          }`}
        >
          {message.text}
        </p>
      )}

      <form onSubmit={submit} className="space-y-4">
        {mode === "register" && (
          <input name="name" placeholder="Name" value={form.name} onChange={change} required className={input} />
        )}
        <input name="email" type="email" placeholder="Email" value={form.email} onChange={change} required className={input} />
        <input
          name="password"
          type="password"
          placeholder="Password (min 6 characters)"
          value={form.password}
          onChange={change}
          required
          minLength={6}
          className={input}
        />
        <button
          disabled={loading}
          className="w-full rounded-lg bg-indigo-600 py-2 font-semibold text-white hover:bg-indigo-700 disabled:opacity-60"
        >
          {loading ? "Please wait..." : mode === "login" ? "Login" : "Create account"}
        </button>
      </form>
    </Page>
  );
}

// Centered white card used by every screen
function Page({ children }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100 p-4">
      <div className="w-full max-w-sm rounded-2xl bg-white p-8 shadow-lg">{children}</div>
    </div>
  );
}
