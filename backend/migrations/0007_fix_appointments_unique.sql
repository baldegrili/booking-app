-- Удаляем старый уникальный индекс (если есть)
DROP INDEX IF EXISTS sqlite_autoindex_appointments_1;

-- Создаём частичный уникальный индекс:
-- уникальность (tenant_id, slot_id) только для активных записей
CREATE UNIQUE INDEX IF NOT EXISTS idx_appointments_active_unique 
ON appointments(tenant_id, slot_id) 
WHERE status != 'cancelled';
