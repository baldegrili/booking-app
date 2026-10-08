-- Добавляем поля в tenants
ALTER TABLE tenants ADD COLUMN owner_telegram_id TEXT;
ALTER TABLE tenants ADD COLUMN owner_max_id TEXT;
ALTER TABLE tenants ADD COLUMN address TEXT;
ALTER TABLE tenants ADD COLUMN phone TEXT;
ALTER TABLE tenants ADD COLUMN working_hours TEXT;
ALTER TABLE tenants ADD COLUMN logo_url TEXT;
ALTER TABLE tenants ADD COLUMN description TEXT;

-- Добавляем поля в services
ALTER TABLE services ADD COLUMN description TEXT;
ALTER TABLE services ADD COLUMN photo_url TEXT;

-- Добавляем поле в appointments (для отметки "был/не пришёл")
ALTER TABLE appointments ADD COLUMN visited INTEGER DEFAULT 0;

-- Заполняем тестовыми данными
UPDATE tenants SET 
    address = 'г. Москва, ул. Ленина, д. 10',
    phone = '+7 (999) 123-45-67',
    working_hours = 'Пн–Сб: 9:00–20:00',
    description = 'Ремонт и обслуживание автомобилей любых марок.'
WHERE id = 1;

UPDATE services SET 
    description = 'Полная замена моторного масла и фильтра'
WHERE id = 1;

UPDATE services SET 
    description = 'Компьютерная диагностика всех систем автомобиля'
WHERE id = 2;

UPDATE services SET 
    description = 'Снятие, балансировка и установка колёс'
WHERE id = 3;