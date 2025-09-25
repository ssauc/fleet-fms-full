"use client";
import { useEffect, useState } from "react";
type Driver = { id:string, full_name:string };
export default function Drivers(){
  const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const H = { Authorization: `Bearer ${token}`, "Content-Type":"application/json" } as any;
  const [rows, setRows] = useState<Driver[]>([]);
  const [name, setName] = useState("");
  const load = async () => {
    const r = await fetch(`${API}/drivers`, { headers: H });
    if (r.ok) setRows(await r.json());
  };
  useEffect(()=>{ if (token) load(); }, [token]);
  const createD = async () => {
    if (!name) return;
    const r = await fetch(`${API}/drivers`, { method:"POST", headers: H, body: JSON.stringify({ full_name:name }) });
    if (r.ok) { setName(""); load(); }
  };
  return (
    <main style={{padding:24}}>
      <h1 style={{fontSize:24, fontWeight:'bold'}}>Drivers</h1>
      <div style={{display:'flex', gap:8, marginTop:12}}>
        <input placeholder="Full name" value={name} onChange={e=>setName(e.target.value)} style={{padding:8, border:'1px solid #ccc'}}/>
        <button onClick={createD} style={{padding:'8px 12px', border:'1px solid #333'}}>Add</button>
      </div>
      <ul style={{marginTop:16}}>
        {rows.map(d => <li key={d.id}>{d.full_name}</li>)}
      </ul>
    </main>
  );
}
