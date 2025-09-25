"use client";
import { useEffect, useState } from "react";
type Alert = { id:string, key:string, status:string, triggered_at:string };
export default function Alerts(){
  const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const H = { Authorization: `Bearer ${token}`, "Content-Type":"application/json" } as any;
  const [rows, setRows] = useState<Alert[]>([]);
  const load = async () => {
    const r = await fetch(`${API}/alerts`, { headers: H });
    if (r.ok) setRows(await r.json());
  };
  useEffect(()=>{ if (token) load(); }, [token]);
  return (
    <main style={{padding:24}}>
      <h1 style={{fontSize:24, fontWeight:'bold'}}>Alerts</h1>
      <ul style={{marginTop:12}}>
        {rows.map(a => (
          <li key={a.id} style={{display:'flex', gap:12, alignItems:'center', borderBottom:'1px solid #eee', padding:'8px 0'}}>
            <div><b>{a.key}</b> — {new Date(a.triggered_at).toLocaleString()} — {a.status}</div>
          </li>
        ))}
      </ul>
    </main>
  );
}
