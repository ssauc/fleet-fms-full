"use client";
import { useState, useEffect } from "react";
export default function Page(){
  const [stats, setStats] = useState<any>({});
  const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

  useEffect(()=>{
    async function load(){
      const headers = { Authorization: `Bearer ${token}` };
      const [v, w, a] = await Promise.all([
        fetch(`${API}/vehicles`, {headers}),
        fetch(`${API}/work-orders`, {headers}),
        fetch(`${API}/alerts`, {headers})
      ]);
      const [vj, wj, aj] = await Promise.all([v.json(), w.json(), a.json()]);
      setStats({
        vehicles: vj.length,
        openWOs: wj.filter((x:any)=>x.status!=="closed").length,
        alerts: aj.length
      });
    }
    if (token) load();
  }, [token]);

  return (
    <main style={{padding:24}}>
      <h1 style={{fontSize:24, fontWeight:'bold'}}>Dashboard</h1>
      <div style={{display:'flex', gap:16, marginTop:12}}>
        <Card label="Vehicles" value={stats.vehicles ?? '-'} />
        <Card label="Open WOs" value={stats.openWOs ?? '-'} />
        <Card label="Alerts" value={stats.alerts ?? '-'} />
      </div>
      <p style={{marginTop:24, color:'#666'}}>Tip: Sign up / login on first run from the Vehicles page.</p>
    </main>
  );
}
function Card({label, value}:{label:string, value:any}){
  return (
    <div style={{border:'1px solid #eee', borderRadius:8, padding:16, minWidth:140}}>
      <div style={{fontSize:12, color:'#777'}}>{label}</div>
      <div style={{fontSize:22, fontWeight:'bold'}}>{value}</div>
    </div>
  );
}
