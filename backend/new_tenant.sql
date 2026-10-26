-- Добавление тенанта: Автосервис Новосибирск
INSERT INTO tenants (name, address, phone, description, owner_telegram_id, slot_duration, working_hours) VALUES ('Автосервис Новосибирск', 'г. Новосибирск, ул. Ленина, д. 1', '+7(913)123-45-67', 'Ремонт', '1', 120, 'Пн–Сб: 9:00–20:00');
-- Услуги для Автосервис Новосибирск
-- График работы для Автосервис Новосибирск
INSERT INTO schedules (tenant_id, day_of_week, start_time, end_time, is_working) VALUES ((SELECT id FROM tenants WHERE name = 'Автосервис Новосибирск' ORDER BY id DESC LIMIT 1), 0, '09:00', '20:00', 1);
INSERT INTO schedules (tenant_id, day_of_week, start_time, end_time, is_working) VALUES ((SELECT id FROM tenants WHERE name = 'Автосервис Новосибирск' ORDER BY id DESC LIMIT 1), 1, '09:00', '20:00', 1);
INSERT INTO schedules (tenant_id, day_of_week, start_time, end_time, is_working) VALUES ((SELECT id FROM tenants WHERE name = 'Автосервис Новосибирск' ORDER BY id DESC LIMIT 1), 2, '09:00', '20:00', 1);
INSERT INTO schedules (tenant_id, day_of_week, start_time, end_time, is_working) VALUES ((SELECT id FROM tenants WHERE name = 'Автосервис Новосибирск' ORDER BY id DESC LIMIT 1), 3, '09:00', '20:00', 1);
INSERT INTO schedules (tenant_id, day_of_week, start_time, end_time, is_working) VALUES ((SELECT id FROM tenants WHERE name = 'Автосервис Новосибирск' ORDER BY id DESC LIMIT 1), 4, '09:00', '20:00', 1);
INSERT INTO schedules (tenant_id, day_of_week, start_time, end_time, is_working) VALUES ((SELECT id FROM tenants WHERE name = 'Автосервис Новосибирск' ORDER BY id DESC LIMIT 1), 5, '09:00', '20:00', 1);
INSERT INTO schedules (tenant_id, day_of_week, start_time, end_time, is_working) VALUES ((SELECT id FROM tenants WHERE name = 'Автосервис Новосибирск' ORDER BY id DESC LIMIT 1), 6, '00:00', '00:00', 0);