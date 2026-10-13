-- Добавляем telegram_id (ID клиента в Telegram)
ALTER TABLE appointments ADD COLUMN telegram_id TEXT;

-- Индекс для быстрого поиска записей клиента
CREATE INDEX IF NOT EXISTS idx_appointments_telegram 
ON appointments(telegram_id);