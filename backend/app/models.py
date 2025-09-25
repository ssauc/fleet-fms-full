from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from .db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(320), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    role = Column(String(32), default="manager")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Driver(Base):
    __tablename__ = "drivers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(200), nullable=False)
    email = Column(String(320))
    phone = Column(String(50))
    license_no = Column(String(64))
    license_class = Column(String(32))
    license_expires_on = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    unit_no = Column(String(64), unique=True, nullable=False)
    vin = Column(String(64))
    make = Column(String(64))
    model = Column(String(64))
    year = Column(Integer)
    class_ = Column(String(64))
    status = Column(String(32), default="in_service")
    meter_type = Column(String(16), default="odometer")
    current_meter = Column(Numeric(12,1), default=0)
    in_service_on = Column(DateTime(timezone=True))
    out_service_on = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class VehicleAssignment(Base):
    __tablename__ = "vehicle_assignments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey('vehicles.id', ondelete='CASCADE'))
    driver_id = Column(UUID(as_uuid=True), ForeignKey('drivers.id', ondelete='SET NULL'))
    start_at = Column(DateTime(timezone=True), server_default=func.now())
    end_at = Column(DateTime(timezone=True))

class MeterReading(Base):
    __tablename__ = "meter_readings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey('vehicles.id', ondelete='CASCADE'))
    type = Column(String(16), nullable=False)  # odometer|hours
    reading = Column(Numeric(12,1), nullable=False)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    source = Column(String(32), default="manual")

class MaintenanceSchedule(Base):
    __tablename__ = "maintenance_schedules"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey('vehicles.id', ondelete='CASCADE'))
    rule_type = Column(String(16), nullable=False)  # mileage|hours|date
    interval_value = Column(Integer, nullable=False)
    last_meter = Column(Numeric(12,1))
    last_completed_at = Column(DateTime(timezone=True))

class WorkOrder(Base):
    __tablename__ = "work_orders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey('vehicles.id', ondelete='CASCADE'))
    title = Column(String(200), nullable=False)
    status = Column(String(32), default='open')
    priority = Column(String(16), default='normal')
    opened_at = Column(DateTime(timezone=True), server_default=func.now())
    due_at = Column(DateTime(timezone=True))
    closed_at = Column(DateTime(timezone=True))

class WorkOrderTask(Base):
    __tablename__ = "wo_tasks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    work_order_id = Column(UUID(as_uuid=True), ForeignKey('work_orders.id', ondelete='CASCADE'))
    title = Column(String(200), nullable=False)
    status = Column(String(32), default='pending')
    est_hours = Column(Numeric(6,2))
    actual_hours = Column(Numeric(6,2))

class Inspection(Base):
    __tablename__ = "inspections"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey('vehicles.id', ondelete='CASCADE'))
    driver_id = Column(UUID(as_uuid=True), ForeignKey('drivers.id', ondelete='SET NULL'))
    checklist_key = Column(String(64), nullable=False)
    result = Column(String(16), nullable=False)  # pass|fail
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

class Defect(Base):
    __tablename__ = "defects"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inspection_id = Column(UUID(as_uuid=True), ForeignKey('inspections.id', ondelete='SET NULL'))
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey('vehicles.id', ondelete='CASCADE'))
    description = Column(Text, nullable=False)
    severity = Column(String(16), default='minor')
    status = Column(String(16), default='open')  # open|in_wo|resolved
    work_order_id = Column(UUID(as_uuid=True), ForeignKey('work_orders.id', ondelete='SET NULL'))

class FuelLog(Base):
    __tablename__ = "fuel_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey('vehicles.id', ondelete='CASCADE'))
    driver_id = Column(UUID(as_uuid=True), ForeignKey('drivers.id', ondelete='SET NULL'))
    qty_gal = Column(Numeric(8,3), nullable=False)
    price_per_gal = Column(Numeric(8,3))
    total_cost = Column(Numeric(12,2))
    odometer = Column(Numeric(12,1))
    vendor = Column(String(64))
    transacted_at = Column(DateTime(timezone=True), server_default=func.now())

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String(64), nullable=False)
    entity_type = Column(String(32), nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    status = Column(String(16), default='open')
    triggered_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True))
