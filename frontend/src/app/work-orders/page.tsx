"use client";
import { useEffect, useState } from "react";
type WO = { id:string, title:string, status:string, vehicle_id:string };
export default function WorkOrders(){
  const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const H = { Authorization: `Bearer ${token}`, "Content-Type":"application/json" } as any;
  const [items, setItems] = useState<WO[]>([]);
  const load = async () => {
    const r = await fetch(`${API}/work-orders`, { headers: H });
    if (r.ok) setItems(await r.json());
  };
  useEffect(()=>{ if (token) load(); }, [token]);
  const setStatus = async (id:string, status:string) => {
    await fetch(`${API}/work-orders/${id}`, { method:"PATCH", headers: H, body: JSON.stringify({ status }) });
    load();
  };
  const col = (s:string) => items.filter(x=>x.status===s);
  const name = (s:string) => s.replace("_"," ");
  return (
    <main style={{padding:24}}>
      <h1 style={{fontSize:24, fontWeight:'bold'}}>Work Orders</h1>
      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr 1fr 1fr', gap:16, marginTop:12}}>
        {["open","in_progress","closed","canceled"].map(s => (
          <div key={s} style={{border:'1px solid #eee', borderRadius:8, padding:12}}>
            <h2 style={{textTransform:'capitalize', fontWeight:'bold'}}>{name(s)}</h2>
            <ul style={{marginTop:8, display:'grid', gap:8}}>
              {col(s).map(w => (
                <li key={w.id} style={{border:'1px solid #ddd', padding:8, borderRadius:6}}>
                  <div style={{fontWeight:'bold'}}>{w.title}</div>
                  <div style={{fontSize:12, color:'#666'}}>Vehicle: <a href={`/vehicles/${w.vehicle_id}`}>{w.vehicle_id}</a></div>
                  <div style={{display:'flex', gap:6, marginTop:6}}>
                    {["open","in_progress","closed","canceled"].filter(x=>x!==s).map(x => (
                      <button key={x} onClick={()=>setStatus(w.id, x)} style={{border:'1px solid #ccc', padding:'4px 8px'}}>{name(x)}</button>
                    ))}
                  </div>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </main>
  );
}
