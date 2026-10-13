-- Индексы для appointments
CREATE INDEX IF NOT EXISTS idx_appointments_tenant 
ON appointments(tenant_id);

CREATE INDEX IF NOT EXISTS idx_appointments_status 
ON appointments(status);

-- Индексы для services
CREATE INDEX IF NOT EXISTS idx_services_tenant 
ON services(tenant_id);

-- Индексы для slots
CREATE INDEX IF NOT EXISTS idx_slots_tenant_booked 
ON slots(tenant_id, is_booked);