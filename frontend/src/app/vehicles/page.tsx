"use client";
import { useEffect, useState } from "react";
type Vehicle = { id: string; unit_no: string; current_meter?: number };
export default function Vehicles() {
  const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const [token, setToken] = useState<string | null>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [unit, setUnit] = useState("");
  const [rows, setRows] = useState<Vehicle[]>([]);
  useEffect(() => {
    setToken(localStorage.getItem("token"));
  }, []);
  const signup = async () => {
    await fetch(`${API}/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, role: "admin" }),
    });
    alert("User created. Now login.");
  };
  const login = async () => {
    const r = await fetch(`${API}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!r.ok) return alert("Login failed");
    const j = await r.json();
    localStorage.setItem("token", j.access_token);
    setToken(j.access_token);
    load();
  };
  const load = async () => {
    const r = await fetch(`${API}/vehicles`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (r.ok) setRows(await r.json());
  };
  useEffect(() => {
    if (token) load();
  }, [token]);
  const createV = async () => {
    const r = await fetch(`${API}/vehicles`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ unit_no: unit }),
    });
    if (r.ok) {
      setUnit("");
      load();
    }
  };
  return (
    <main style={{ padding: 24 }}>
      <h1 style={{ fontSize: 24, fontWeight: "bold" }}>Vehicles</h1>
      {!token && (
        <div
          style={{
            display: "flex",
            gap: 8,
            alignItems: "center",
            margin: "12px 0",
          }}
        >
          <input
            placeholder="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={{ padding: 8, border: "1px solid #ccc" }}
          />
          <input
            type="password"
            placeholder="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{ padding: 8, border: "1px solid #ccc" }}
          />
          <button
            onClick={signup}
            style={{ padding: "8px 12px", border: "1px solid #333" }}
          >
            Sign up
          </button>
          <button
            onClick={login}
            style={{ padding: "8px 12px", border: "1px solid #333" }}
          >
            Login
          </button>
        </div>
      )}
      <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
        <input
          placeholder="Unit #"
          value={unit}
          onChange={(e) => setUnit(e.target.value)}
          style={{ padding: 8, border: "1px solid #ccc" }}
        />
        <button
          onClick={createV}
          style={{ padding: "8px 12px", border: "1px solid #333" }}
        >
          Add
        </button>
      </div>
      <ul style={{ marginTop: 16 }}>
        {rows.map((v) => (
          <li key={v.id}>
            <a href={`/vehicles/${v.id}`}>{v.unit_no}</a>{" "}
            {typeof v.current_meter !== "undefined"
              ? `— ${v.current_meter}`
              : ""}
          </li>
        ))}
      </ul>
    </main>
  );
}
