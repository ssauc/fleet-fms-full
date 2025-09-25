from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from datetime import datetime, timezone, timedelta

from .settings import settings
from .db import SessionLocal, Base, engine
from .models import (User, Driver, Vehicle, VehicleAssignment, MeterReading,
                     MaintenanceSchedule, WorkOrder, WorkOrderTask,
                     Inspection, Defect, FuelLog, Alert)
from .auth import hash_password, verify_password, create_token, ALGO

app = FastAPI(title=settings.project_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.allowed_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_db():
    async with SessionLocal() as s:
        yield s

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Auth
class SignupIn(BaseModel):
    email: str
    password: str
    role: str = "manager"

@app.post("/auth/signup")
async def signup(data: SignupIn, db: AsyncSession = Depends(get_db)):
    exists = (await db.execute(select(User).where(User.email == data.email))).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    u = User(email=data.email, password_hash=hash_password(data.password), role=data.role)
    db.add(u); await db.commit()
    return {"ok": True}

class LoginIn(BaseModel):
    email: str
    password: str

@app.post("/auth/login")
async def login(data: LoginIn, db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(User).where(User.email == data.email))).scalar_one_or_none()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_token(str(user.id), user.role), "token_type": "bearer"}

async def require_user(authorization: Optional[str] = Header(default=None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization.split()[1]
    try:
        payload = jwt.decode(token, settings.api_jwt_secret, algorithms=[ALGO])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_role(payload: dict, roles: list[str]):
    if payload.get("role") not in roles:
        raise HTTPException(status_code=403, detail="Forbidden")

# Vehicles
class VehicleIn(BaseModel):
    unit_no: str
    vin: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    class_: Optional[str] = None
    meter_type: Optional[str] = "odometer"

@app.get("/vehicles")
async def list_vehicles(db: AsyncSession = Depends(get_db), user=Depends(require_user)):
    return (await db.execute(select(Vehicle))).scalars().all()

@app.post("/vehicles")
async def create_vehicle(v: VehicleIn, db: AsyncSession = Depends(get_db), user=Depends(require_user)):
    require_role(user, ["admin","manager"])
    obj = Vehicle(**v.model_dump())
    db.add(obj); await db.commit(); await db.refresh(obj)
    return obj

@app.get("/vehicles/{veh_id}")
async def get_vehicle(veh_id: str, db: AsyncSession = Depends(get_db), user=Depends(require_user)):
    row = (await db.execute(select(Vehicle).where(Vehicle.id == veh_id))).scalar_one_or_none()
    if not row: raise HTTPException(status_code=404, detail="Not found")
    return row

# Meters
class MeterIn(BaseModel):
    type: str
    reading: float
    recorded_at: Optional[datetime] = None
    source: Optional[str] = "manual"

@app.get("/vehicles/{veh_id}/meters")
async def list_meters(veh_id: str, db: AsyncSession = Depends(get_db), user=Depends(require_user)):
    return (await db.execute(select(MeterReading).where(MeterReading.vehicle_id == veh_id).order_by(MeterReading.recorded_at.desc()))).scalars().all()

@app.post("/vehicles/{veh_id}/meters")
async def add_meter(veh_id: str, m: MeterIn, db: AsyncSession = Depends(get_db), user=Depends(require_user)):
    v = (await db.execute(select(Vehicle).where(Vehicle.id == veh_id))).scalar_one_or_none()
    if not v: raise HTTPException(status_code=404, detail="Vehicle not found")
    mr = MeterReading(vehicle_id=veh_id, type=m.type, reading=m.reading, recorded_at=m.recorded_at, source=m.source)
    db.add(mr)
    if m.type == 'odometer' and (v.current_meter is None or m.reading >= float(v.current_meter)):
        v.current_meter = m.reading
    await db.commit(); await db.refresh(mr)
    return mr

# Drivers & Assignments
class DriverIn(BaseModel):
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    license_no: Optional[str] = None
    license_class: Optional[str] = None
    license_expires_on: Optional[datetime] = None

@app.get("/drivers")
async def list_drivers(db: AsyncSession = Depends(get_db), user=Depends(require_user)):
    return (await db.execute(select(Driver))).scalars().all()

@app.post("/drivers")
async def create_driver(d: DriverIn, db: AsyncSession = Depends(get_db), user=Depends(require_user)):
    require_role(user, ["admin","manager"])
    row = Driver(**d.model_dump())
    db.add(row); await db.commit(); await db.refresh(row)
    return row

class AssignIn(BaseModel):
    driver_id: str
    start_at: Optional[datetime] = None

@app.post("/vehicles/{veh_id}/assign")
async def assign_driver(veh_id: str, data: AssignIn, db: AsyncSession = Depends(get_db), user=Depends(require_user)):
    require_role(user, ["admin","manager"])
    v = (await db.execute(select(Vehicle).where(Vehicle.id == veh_id))).scalar_one_or_none()
    if not v: raise HTTPException(status_code=404, detail="Vehicle not found")
    a = VehicleAssignment(vehicle_id=veh_id, driver_id=data.driver_id, start_at=data.start_at or datetime.now(timezone.utc))
    db.add(a); await db.commit(); await db.refresh(a)
    return a

# Maintenance & WOs
class ScheduleIn(BaseModel):
    rule_type: str
    interval_value: int

@app.get("/vehicles/{veh_id}/schedules")
async def list_schedules(veh_id: str, db: AsyncSession = Depends(get_db), user=Depends(require_user)):
    return (await db.execute(select(MaintenanceSchedule).where(MaintenanceSchedule.vehicle_id == veh_id))).scalars().all()

@app.post("/vehicles/{veh_id}/schedules")
async def create_schedule(veh_id: str, s: ScheduleIn, db: AsyncSession = Depends(get_db), user=Depends(require_user)):
    require_role(user, ["admin","manager"])
    sc = MaintenanceSchedule(vehicle_id=veh_id, rule_type=s.rule_type, interval_value=s.interval_value)
    db.add(sc); await db.commit(); await db.refresh(sc)
    return sc

class WorkOrderIn(BaseModel):
    vehicle_id: str
    title: str
    priority: Optional[str] = "normal"
    due_at: Optional[datetime] = None

class WorkOrderPatch(BaseModel):
    status: Optional[str] = None

@app.get("/work-orders")
async def list_work_orders(db: AsyncSession = Depends(get_db), user=Depends(require_user)):
    return (await db.execute(select(WorkOrder))).scalars().all()

@app.post("/work-orders")
async def create_work_order(data: WorkOrderIn, db: AsyncSession = Depends(get_db), user=Depends(require_user)):
    wo = WorkOrder(vehicle_id=data.vehicle_id, title=data.title, priority=data.priority, due_at=data.due_at)
    db.add(wo); await db.commit(); await db.refresh(wo)
    return wo

@app.patch("/work-orders/{wo_id}")
async def update_work_order_status(wo_id: str, patch: WorkOrderPatch, db: AsyncSession = Depends(get_db), user=Depends(require_user)):
    row = (await db.execute(select(WorkOrder).where(WorkOrder.id == wo_id))).scalar_one_or_none()
    if not row: raise HTTPException(status_code=404, detail="Not found")
    if patch.status:
        row.status = patch.status
        if patch.status == 'closed':
            row.closed_at = datetime.now(timezone.utc)
    await db.commit(); await db.refresh(row)
    return row

class TaskIn(BaseModel):
    title: str
    est_hours: Optional[float] = None

@app.post("/work-orders/{wo_id}/tasks")
async def add_task(wo_id: str, t: TaskIn, db: AsyncSession = Depends(get_db), user=Depends(require_user)):
    row = (await db.execute(select(WorkOrder).where(WorkOrder.id == wo_id))).scalar_one_or_none()
    if not row: raise HTTPException(status_code=404, detail="WO not found")
    task = WorkOrderTask(work_order_id=wo_id, title=t.title, est_hours=t.est_hours)
    db.add(task); await db.commit(); await db.refresh(task)
    return task

# Inspections & Defects
class InspectionIn(BaseModel):
    checklist_key: str
    result: str
    driver_id: Optional[str] = None

@app.post("/vehicles/{veh_id}/inspections")
async def submit_inspection(veh_id: str, data: InspectionIn, db: AsyncSession = Depends(get_db), user=Depends(require_user)):
    v = (await db.execute(select(Vehicle).where(Vehicle.id == veh_id))).scalar_one_or_none()
    if not v: raise HTTPException(status_code=404, detail="Vehicle not found")
    ins = Inspection(vehicle_id=veh_id, driver_id=data.driver_id, checklist_key=data.checklist_key, result=data.result)
    db.add(ins); await db.commit(); await db.refresh(ins)
    if data.result == 'fail':
        defect = Defect(inspection_id=ins.id, vehicle_id=veh_id, description=f"Failed {data.checklist_key}", severity='major')
        db.add(defect)
        wo = WorkOrder(vehicle_id=veh_id, title=f"Repair from inspection {data.checklist_key}", priority='high')
        db.add(wo)
        await db.commit()
    return ins

# Fuel
class FuelIn(BaseModel):
    driver_id: Optional[str] = None
    qty_gal: float
    price_per_gal: Optional[float] = None
    total_cost: Optional[float] = None
    odometer: Optional[float] = None
    vendor: Optional[str] = None

@app.post("/vehicles/{veh_id}/fuel")
async def add_fuel(veh_id: str, data: FuelIn, db: AsyncSession = Depends(get_db), user=Depends(require_user)):
    v = (await db.execute(select(Vehicle).where(Vehicle.id == veh_id))).scalar_one_or_none()
    if not v: raise HTTPException(status_code=404, detail="Vehicle not found")
    row = FuelLog(vehicle_id=veh_id, driver_id=data.driver_id, qty_gal=data.qty_gal, price_per_gal=data.price_per_gal,
                  total_cost=data.total_cost, odometer=data.odometer, vendor=data.vendor)
    db.add(row); await db.commit(); await db.refresh(row)
    return row

# Alerts & Nightly
@app.get("/alerts")
async def list_alerts(db: AsyncSession = Depends(get_db), user=Depends(require_user)):
    return (await db.execute(select(Alert))).scalars().all()

@app.post("/internal/run-nightly")
async def run_nightly(db: AsyncSession = Depends(get_db), user=Depends(require_user)):
    now = datetime.now(timezone.utc)
    vehicles = (await db.execute(select(Vehicle))).scalars().all()
    for v in vehicles:
        schedules = (await db.execute(select(MaintenanceSchedule).where(MaintenanceSchedule.vehicle_id == v.id))).scalars().all()
        for sc in schedules:
            if sc.rule_type == 'mileage' and v.current_meter and sc.last_meter is not None:
                if float(v.current_meter) - float(sc.last_meter) >= sc.interval_value:
                    db.add(Alert(key='PM_DUE', entity_type='vehicle', entity_id=v.id))
            if sc.rule_type == 'date' and sc.last_completed_at:
                if (now - sc.last_completed_at) >= timedelta(days=sc.interval_value):
                    db.add(Alert(key='PM_DUE', entity_type='vehicle', entity_id=v.id))
    await db.commit()
    return {"ok": True}
