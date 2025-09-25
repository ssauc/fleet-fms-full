from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as psql

revision = '0001_init_full'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")

    op.create_table('users',
        sa.Column('id', psql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(length=320), nullable=False, unique=True),
        sa.Column('password_hash', sa.Text(), nullable=False),
        sa.Column('role', sa.String(length=32), server_default='manager'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )

    op.create_table('drivers',
        sa.Column('id', psql.UUID(as_uuid=True), primary_key=True),
        sa.Column('full_name', sa.String(length=200), nullable=False),
        sa.Column('email', sa.String(length=320)),
        sa.Column('phone', sa.String(length=50)),
        sa.Column('license_no', sa.String(length=64)),
        sa.Column('license_class', sa.String(length=32)),
        sa.Column('license_expires_on', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )

    op.create_table('vehicles',
        sa.Column('id', psql.UUID(as_uuid=True), primary_key=True),
        sa.Column('unit_no', sa.String(length=64), nullable=False, unique=True),
        sa.Column('vin', sa.String(length=64)),
        sa.Column('make', sa.String(length=64)),
        sa.Column('model', sa.String(length=64)),
        sa.Column('year', sa.Integer()),
        sa.Column('class_', sa.String(length=64)),
        sa.Column('status', sa.String(length=32), server_default='in_service'),
        sa.Column('meter_type', sa.String(length=16), server_default='odometer'),
        sa.Column('current_meter', sa.Numeric(12,1), server_default='0'),
        sa.Column('in_service_on', sa.DateTime(timezone=True)),
        sa.Column('out_service_on', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )

    op.create_table('vehicle_assignments',
        sa.Column('id', psql.UUID(as_uuid=True), primary_key=True),
        sa.Column('vehicle_id', psql.UUID(as_uuid=True), sa.ForeignKey('vehicles.id', ondelete='CASCADE')),
        sa.Column('driver_id', psql.UUID(as_uuid=True), sa.ForeignKey('drivers.id', ondelete='SET NULL')),
        sa.Column('start_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('end_at', sa.DateTime(timezone=True))
    )

    op.create_table('meter_readings',
        sa.Column('id', psql.UUID(as_uuid=True), primary_key=True),
        sa.Column('vehicle_id', psql.UUID(as_uuid=True), sa.ForeignKey('vehicles.id', ondelete='CASCADE')),
        sa.Column('type', sa.String(length=16), nullable=False),
        sa.Column('reading', sa.Numeric(12,1), nullable=False),
        sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('source', sa.String(length=32), server_default='manual')
    )

    op.create_table('maintenance_schedules',
        sa.Column('id', psql.UUID(as_uuid=True), primary_key=True),
        sa.Column('vehicle_id', psql.UUID(as_uuid=True), sa.ForeignKey('vehicles.id', ondelete='CASCADE')),
        sa.Column('rule_type', sa.String(length=16), nullable=False),
        sa.Column('interval_value', sa.Integer(), nullable=False),
        sa.Column('last_meter', sa.Numeric(12,1)),
        sa.Column('last_completed_at', sa.DateTime(timezone=True))
    )

    op.create_table('work_orders',
        sa.Column('id', psql.UUID(as_uuid=True), primary_key=True),
        sa.Column('vehicle_id', psql.UUID(as_uuid=True), sa.ForeignKey('vehicles.id', ondelete='CASCADE')),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('status', sa.String(length=32), server_default='open'),
        sa.Column('priority', sa.String(length=16), server_default='normal'),
        sa.Column('opened_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('due_at', sa.DateTime(timezone=True)),
        sa.Column('closed_at', sa.DateTime(timezone=True))
    )

    op.create_table('wo_tasks',
        sa.Column('id', psql.UUID(as_uuid=True), primary_key=True),
        sa.Column('work_order_id', psql.UUID(as_uuid=True), sa.ForeignKey('work_orders.id', ondelete='CASCADE')),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('status', sa.String(length=32), server_default='pending'),
        sa.Column('est_hours', sa.Numeric(6,2)),
        sa.Column('actual_hours', sa.Numeric(6,2))
    )

    op.create_table('inspections',
        sa.Column('id', psql.UUID(as_uuid=True), primary_key=True),
        sa.Column('vehicle_id', psql.UUID(as_uuid=True), sa.ForeignKey('vehicles.id', ondelete='CASCADE')),
        sa.Column('driver_id', psql.UUID(as_uuid=True), sa.ForeignKey('drivers.id', ondelete='SET NULL')),
        sa.Column('checklist_key', sa.String(length=64), nullable=False),
        sa.Column('result', sa.String(length=16), nullable=False),
        sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )

    op.create_table('defects',
        sa.Column('id', psql.UUID(as_uuid=True), primary_key=True),
        sa.Column('inspection_id', psql.UUID(as_uuid=True), sa.ForeignKey('inspections.id', ondelete='SET NULL')),
        sa.Column('vehicle_id', psql.UUID(as_uuid=True), sa.ForeignKey('vehicles.id', ondelete='CASCADE')),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(length=16), server_default='minor'),
        sa.Column('status', sa.String(length=16), server_default='open'),
        sa.Column('work_order_id', psql.UUID(as_uuid=True), sa.ForeignKey('work_orders.id', ondelete='SET NULL'))
    )

    op.create_table('fuel_logs',
        sa.Column('id', psql.UUID(as_uuid=True), primary_key=True),
        sa.Column('vehicle_id', psql.UUID(as_uuid=True), sa.ForeignKey('vehicles.id', ondelete='CASCADE')),
        sa.Column('driver_id', psql.UUID(as_uuid=True), sa.ForeignKey('drivers.id', ondelete='SET NULL')),
        sa.Column('qty_gal', sa.Numeric(8,3), nullable=False),
        sa.Column('price_per_gal', sa.Numeric(8,3)),
        sa.Column('total_cost', sa.Numeric(12,2)),
        sa.Column('odometer', sa.Numeric(12,1)),
        sa.Column('vendor', sa.String(length=64)),
        sa.Column('transacted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )

    op.create_table('alerts',
        sa.Column('id', psql.UUID(as_uuid=True), primary_key=True),
        sa.Column('key', sa.String(length=64), nullable=False),
        sa.Column('entity_type', sa.String(length=32), nullable=False),
        sa.Column('entity_id', psql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(length=16), server_default='open'),
        sa.Column('triggered_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('resolved_at', sa.DateTime(timezone=True))
    )

def downgrade() -> None:
    for t in ['alerts','fuel_logs','defects','inspections','wo_tasks','work_orders','maintenance_schedules','meter_readings','vehicle_assignments','vehicles','drivers','users']:
        op.drop_table(t)
