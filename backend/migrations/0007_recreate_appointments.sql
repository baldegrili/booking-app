-- 1. Создаём новую таблицу без UNIQUE в определении
CREATE TABLE appointments_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    user_name TEXT NOT NULL,
    user_phone TEXT NOT NULL,
    service_id INTEGER NOT NULL,
    slot_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'confirmed',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    visited INTEGER DEFAULT 0,
    telegram_id TEXT,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    FOREIGN KEY (service_id) REFERENCES services(id),
    FOREIGN KEY (slot_id) REFERENCES slots(id)
);

-- 2. Копируем данные из старой таблицы
INSERT INTO appointments_new 
SELECT 
    id, 
    tenant_id, 
    user_name, 
    user_phone, 
    service_id, 
    slot_id, 
    status, 
    created_at, 
    visited, 
    telegram_id 
FROM appointments;

-- 3. Удаляем старую таблицу
DROP TABLE appointments;

-- 4. Переименовываем новую
ALTER TABLE appointments_new RENAME TO appointments;

-- 5. Частичный уникальный индекс: только для активных записей
CREATE UNIQUE INDEX IF NOT EXISTS idx_appointments_active_unique 
ON appointments(tenant_id, slot_id) 
WHERE status != 'cancelled';

-- 6. Возвращаем обычные индексы
CREATE INDEX IF NOT EXISTS idx_appointments_tenant ON appointments(tenant_id);
CREATE INDEX IF NOT EXISTS idx_appointments_telegram ON appointments(telegram_id);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);