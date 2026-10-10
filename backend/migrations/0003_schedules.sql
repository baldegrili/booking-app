-- Настройки генерации слотов в tenants
ALTER TABLE tenants ADD COLUMN slot_duration INTEGER DEFAULT 120;
ALTER TABLE tenants ADD COLUMN generation_days_ahead INTEGER DEFAULT 30;

-- Таблица графиков работы по дням недели
CREATE TABLE IF NOT EXISTS schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    start_time TEXT NOT NULL DEFAULT '09:00',
    end_time TEXT NOT NULL DEFAULT '20:00',
    is_working INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    UNIQUE(tenant_id, day_of_week)
);

-- Уникальный индекс на слоты
CREATE UNIQUE INDEX IF NOT EXISTS idx_slots_tenant_datetime 
ON slots(tenant_id, datetime);