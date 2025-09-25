"use client";
import { useEffect, useState } from "react";
export default function VehicleDetail({ params }: any){
  const { id } = params;
  const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const H = { Authorization: `Bearer ${token}`, "Content-Type":"application/json" } as any;
  const [veh, setVeh] = useState<any>(null);
  const [meters, setMeters] = useState<any[]>([]);
  const [schedules, setSchedules] = useState<any[]>([]);
  const [wo, setWo] = useState<any[]>([]);
  const [meterType, setMeterType] = useState("odometer");
  const [meterVal, setMeterVal] = useState("");
  const [woTitle, setWoTitle] = useState("");
  const load = async () => {
    const [a,b,c,d] = await Promise.all([
      fetch(`${API}/vehicles/${id}`, { headers: H }),
      fetch(`${API}/vehicles/${id}/meters`, { headers: H }),
      fetch(`${API}/vehicles/${id}/schedules`, { headers: H }),
      fetch(`${API}/work-orders`, { headers: H }),
    ]);
    const [aj,bj,cj,dj] = await Promise.all([a.json(), b.json(), c.json(), d.json()]);
    setVeh(aj);
    setMeters(bj);
    setSchedules(cj.filter((x:any)=>x.vehicle_id===id));
    setWo(dj.filter((x:any)=>x.vehicle_id===id));
  };
  useEffect(()=>{ if (token) load(); }, [token, id]);
  const addMeter = async () => {
    if (!meterVal) return;
    const r = await fetch(`${API}/vehicles/${id}/meters`, { method:"POST", headers: H, body: JSON.stringify({ type: meterType, reading: parseFloat(meterVal) }) });
    if (r.ok) { setMeterVal(""); load(); }
  };
  const createWO = async () => {
    if (!woTitle) return;
    const r = await fetch(`${API}/work-orders`, { method:"POST", headers: H, body: JSON.stringify({ vehicle_id: id, title: woTitle }) });
    if (r.ok) { setWoTitle(""); load(); }
  };
  const addSchedule = async () => {
    const interval = prompt("Interval value (miles/days/hours):", "5000");
    if (!interval) return;
    const type = prompt("Rule type: mileage | hours | date", "mileage") || "mileage";
    const r = await fetch(`${API}/vehicles/${id}/schedules`, { method:"POST", headers: H, body: JSON.stringify({ rule_type: type, interval_value: parseInt(interval) }) });
    if (r.ok) load();
  };
  if (!veh) return <main style={{padding:24}}>Loading…</main>;
  return (
    <main style={{padding:24}}>
      <h1 style={{fontSize:24, fontWeight:'bold'}}>Vehicle {veh.unit_no}</h1>
      <div style={{color:'#666'}}>VIN: {veh.vin || '—'} • Meter: {veh.current_meter ?? '—'}</div>
      <section style={{marginTop:16}}>
        <h2 style={{fontWeight:'bold'}}>Add Meter</h2>
        <div style={{display:'flex', gap:8, alignItems:'center'}}>
          <select value={meterType} onChange={e=>setMeterType(e.target.value)}>
            <option value="odometer">Odometer</option>
            <option value="hours">Hours</option>
          </select>
          <input placeholder="Reading" value={meterVal} onChange={e=>setMeterVal(e.target.value)} style={{padding:8, border:'1px solid #ccc'}} />
          <button onClick={addMeter} style={{padding:'8px 12px', border:'1px solid #333'}}>Save</button>
        </div>
        <ul style={{marginTop:8}}>
          {meters.map(m => <li key={m.id}>{m.type}: {m.reading} at {new Date(m.recorded_at).toLocaleString()}</li>)}
        </ul>
      </section>
      <section style={{marginTop:16}}>
        <h2 style={{fontWeight:'bold'}}>Maintenance</h2>
        <button onClick={addSchedule} style={{padding:'6px 10px', border:'1px solid #333'}}>Add Schedule</button>
        <ul>
          {schedules.map(s => <li key={s.id}>{s.rule_type} every {s.interval_value}</li>)}
        </ul>
      </section>
      <section style={{marginTop:16}}>
        <h2 style={{fontWeight:'bold'}}>Work Orders</h2>
        <div style={{display:'flex', gap:8}}>
          <input placeholder="Title" value={woTitle} onChange={e=>setWoTitle(e.target.value)} style={{padding:8, border:'1px solid #ccc'}}/>
          <button onClick={createWO} style={{padding:'8px 12px', border:'1px solid #333'}}>Create</button>
        </div>
        <ul style={{marginTop:8}}>
          {wo.map((x:any) => <li key={x.id}>{x.title} — {x.status}</li>)}
        </ul>
      </section>
    </main>
  );
}
