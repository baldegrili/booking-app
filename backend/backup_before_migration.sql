PRAGMA defer_foreign_keys=TRUE;
CREATE TABLE tenants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
, owner_telegram_id TEXT, owner_max_id TEXT, address TEXT, phone TEXT, working_hours TEXT, logo_url TEXT, description TEXT, slot_duration INTEGER DEFAULT 120, generation_days_ahead INTEGER DEFAULT 30);
INSERT INTO "tenants" ("id","name","owner_telegram_id","owner_max_id","address","phone","working_hours","logo_url","description","slot_duration","generation_days_ahead") VALUES(1,'Автосервис на Ленина','5072334101',NULL,'г. Москва, ул. Ленина, д. 10','+7 (999) 123-45-67','Пн–Сб: 9:00–20:00',NULL,'Ремонт и обслуживание автомобилей любых марок.',120,30);
CREATE TABLE services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    price REAL NOT NULL, description TEXT, photo_url TEXT,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);
INSERT INTO "services" ("id","tenant_id","name","price","description","photo_url") VALUES(1,1,'Замена масла',1500,'Полная замена моторного масла и фильтра',NULL);
INSERT INTO "services" ("id","tenant_id","name","price","description","photo_url") VALUES(2,1,'Диагностика',2000,'Компьютерная диагностика всех систем автомобиля',NULL);
INSERT INTO "services" ("id","tenant_id","name","price","description","photo_url") VALUES(3,1,'Шиномонтаж',2500,'Снятие, балансировка и установка колёс',NULL);
INSERT INTO "services" ("id","tenant_id","name","price","description","photo_url") VALUES(5,1,'тоси боси',10000,'там сям',NULL);
CREATE TABLE slots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    datetime TEXT NOT NULL,
    is_booked INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(1,1,'2026-10-10 10:00',1);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(2,1,'2026-10-10 12:00',1);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(3,1,'2026-10-11 14:00',1);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(4,1,'2026-10-15 10:00',1);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(5,1,'2026-10-15 12:00',1);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(6,1,'2026-10-15 14:00',1);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(7,1,'2026-10-16 10:00',1);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(8,1,'2026-10-16 12:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(9,1,'2026-10-12 09:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(10,1,'2026-10-12 11:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(11,1,'2026-10-12 13:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(12,1,'2026-10-12 15:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(13,1,'2026-10-12 17:00',1);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(14,1,'2026-10-13 09:00',1);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(15,1,'2026-10-13 11:00',1);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(16,1,'2026-10-13 13:00',1);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(17,1,'2026-10-13 15:00',1);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(18,1,'2026-10-13 17:00',1);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(19,1,'2026-10-14 09:00',1);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(20,1,'2026-10-14 11:00',1);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(21,1,'2026-10-14 13:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(22,1,'2026-10-14 15:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(23,1,'2026-10-14 17:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(24,1,'2026-10-15 09:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(25,1,'2026-10-15 11:00',1);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(26,1,'2026-10-15 13:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(27,1,'2026-10-15 15:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(28,1,'2026-10-15 17:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(29,1,'2026-10-16 09:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(30,1,'2026-10-16 11:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(31,1,'2026-10-16 13:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(32,1,'2026-10-16 15:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(33,1,'2026-10-16 17:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(34,1,'2026-10-17 10:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(35,1,'2026-10-17 12:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(36,1,'2026-10-17 14:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(37,1,'2026-10-17 16:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(38,1,'2026-10-19 09:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(39,1,'2026-10-19 11:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(40,1,'2026-10-19 13:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(41,1,'2026-10-19 15:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(42,1,'2026-10-19 17:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(43,1,'2026-10-20 09:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(44,1,'2026-10-20 11:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(45,1,'2026-10-20 13:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(46,1,'2026-10-20 15:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(47,1,'2026-10-20 17:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(48,1,'2026-10-21 09:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(49,1,'2026-10-21 11:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(50,1,'2026-10-21 13:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(51,1,'2026-10-21 15:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(52,1,'2026-10-21 17:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(53,1,'2026-10-22 09:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(54,1,'2026-10-22 11:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(55,1,'2026-10-22 13:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(56,1,'2026-10-22 15:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(57,1,'2026-10-22 17:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(58,1,'2026-10-23 09:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(59,1,'2026-10-23 11:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(60,1,'2026-10-23 13:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(61,1,'2026-10-23 15:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(62,1,'2026-10-23 17:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(63,1,'2026-10-24 10:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(64,1,'2026-10-24 12:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(65,1,'2026-10-24 14:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(66,1,'2026-10-24 16:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(67,1,'2026-10-26 09:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(68,1,'2026-10-26 11:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(69,1,'2026-10-26 13:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(70,1,'2026-10-26 15:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(71,1,'2026-10-26 17:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(72,1,'2026-10-27 09:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(73,1,'2026-10-27 11:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(74,1,'2026-10-27 13:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(75,1,'2026-10-27 15:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(76,1,'2026-10-27 17:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(77,1,'2026-10-28 09:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(78,1,'2026-10-28 11:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(79,1,'2026-10-28 13:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(80,1,'2026-10-28 15:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(81,1,'2026-10-28 17:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(82,1,'2026-10-29 09:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(83,1,'2026-10-29 11:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(84,1,'2026-10-29 13:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(85,1,'2026-10-29 15:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(86,1,'2026-10-29 17:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(87,1,'2026-10-30 09:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(88,1,'2026-10-30 11:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(89,1,'2026-10-30 13:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(90,1,'2026-10-30 15:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(91,1,'2026-10-30 17:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(92,1,'2026-10-31 10:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(93,1,'2026-10-31 12:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(94,1,'2026-10-31 14:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(95,1,'2026-10-31 16:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(96,1,'2026-11-02 09:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(97,1,'2026-11-02 11:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(98,1,'2026-11-02 13:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(99,1,'2026-11-02 15:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(100,1,'2026-11-02 17:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(101,1,'2026-11-03 09:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(102,1,'2026-11-03 11:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(103,1,'2026-11-03 13:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(104,1,'2026-11-03 15:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(105,1,'2026-11-03 17:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(106,1,'2026-11-04 09:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(107,1,'2026-11-04 11:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(108,1,'2026-11-04 13:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(109,1,'2026-11-04 15:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(110,1,'2026-11-04 17:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(111,1,'2026-11-05 09:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(112,1,'2026-11-05 11:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(113,1,'2026-11-05 13:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(114,1,'2026-11-05 15:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(115,1,'2026-11-05 17:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(116,1,'2026-11-06 09:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(117,1,'2026-11-06 11:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(118,1,'2026-11-06 13:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(119,1,'2026-11-06 15:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(120,1,'2026-11-06 17:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(121,1,'2026-11-07 10:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(122,1,'2026-11-07 12:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(123,1,'2026-11-07 14:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(124,1,'2026-11-07 16:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(125,1,'2026-11-09 09:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(126,1,'2026-11-09 11:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(127,1,'2026-11-09 13:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(128,1,'2026-11-09 15:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(129,1,'2026-11-09 17:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(2666,1,'2026-11-10 09:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(2667,1,'2026-11-10 11:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(2668,1,'2026-11-10 13:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(2669,1,'2026-11-10 15:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(2670,1,'2026-11-10 17:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(2671,1,'2026-11-11 09:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(2672,1,'2026-11-11 11:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(2673,1,'2026-11-11 13:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(2674,1,'2026-11-11 15:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(2675,1,'2026-11-11 17:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(3049,1,'2026-11-12 09:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(3050,1,'2026-11-12 11:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(3051,1,'2026-11-12 13:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(3052,1,'2026-11-12 15:00',0);
INSERT INTO "slots" ("id","tenant_id","datetime","is_booked") VALUES(3053,1,'2026-11-12 17:00',0);
CREATE TABLE appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    user_name TEXT NOT NULL,
    user_phone TEXT NOT NULL,
    service_id INTEGER NOT NULL,
    slot_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'confirmed',
    created_at TEXT NOT NULL DEFAULT (datetime('now')), visited INTEGER DEFAULT 0, telegram_id TEXT,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    FOREIGN KEY (service_id) REFERENCES services(id),
    FOREIGN KEY (slot_id) REFERENCES slots(id),
    UNIQUE(tenant_id, slot_id)
);
INSERT INTO "appointments" ("id","tenant_id","user_name","user_phone","service_id","slot_id","status","created_at","visited","telegram_id") VALUES(1,1,'Андрей','+79952714019',1,1,'confirmed','2026-10-07 14:19:47',0,NULL);
INSERT INTO "appointments" ("id","tenant_id","user_name","user_phone","service_id","slot_id","status","created_at","visited","telegram_id") VALUES(2,1,'Андрей','+79952714019',1,2,'confirmed','2026-10-08 12:50:22',0,NULL);
INSERT INTO "appointments" ("id","tenant_id","user_name","user_phone","service_id","slot_id","status","created_at","visited","telegram_id") VALUES(3,1,'Андрей','+79952714019',1,3,'confirmed','2026-10-09 14:31:01',0,NULL);
INSERT INTO "appointments" ("id","tenant_id","user_name","user_phone","service_id","slot_id","status","created_at","visited","telegram_id") VALUES(4,1,'Андрей','+79952714019',3,4,'confirmed','2026-10-09 14:39:43',0,NULL);
INSERT INTO "appointments" ("id","tenant_id","user_name","user_phone","service_id","slot_id","status","created_at","visited","telegram_id") VALUES(5,1,'Андрей','+79952714019',1,5,'confirmed','2026-10-09 14:41:53',0,NULL);
INSERT INTO "appointments" ("id","tenant_id","user_name","user_phone","service_id","slot_id","status","created_at","visited","telegram_id") VALUES(6,1,'Андрей','+79952714019',1,6,'confirmed','2026-10-09 14:47:55',0,NULL);
INSERT INTO "appointments" ("id","tenant_id","user_name","user_phone","service_id","slot_id","status","created_at","visited","telegram_id") VALUES(7,1,'Андрей','+79952714019',5,19,'confirmed','2026-10-11 11:38:40',0,NULL);
INSERT INTO "appointments" ("id","tenant_id","user_name","user_phone","service_id","slot_id","status","created_at","visited","telegram_id") VALUES(8,1,'Андрей','+79952714019',5,25,'confirmed','2026-10-11 11:43:11',0,NULL);
INSERT INTO "appointments" ("id","tenant_id","user_name","user_phone","service_id","slot_id","status","created_at","visited","telegram_id") VALUES(9,1,'Андрей','+79952714019',3,14,'confirmed','2026-10-11 11:50:48',0,NULL);
INSERT INTO "appointments" ("id","tenant_id","user_name","user_phone","service_id","slot_id","status","created_at","visited","telegram_id") VALUES(10,1,'Андрей','+79952714019',3,15,'confirmed','2026-10-11 11:50:58',0,NULL);
INSERT INTO "appointments" ("id","tenant_id","user_name","user_phone","service_id","slot_id","status","created_at","visited","telegram_id") VALUES(11,1,'Андрей','+79952714019',2,16,'confirmed','2026-10-11 11:51:05',0,NULL);
INSERT INTO "appointments" ("id","tenant_id","user_name","user_phone","service_id","slot_id","status","created_at","visited","telegram_id") VALUES(12,1,'Андрей','+79952714019',5,18,'confirmed','2026-10-11 11:59:38',0,NULL);
INSERT INTO "appointments" ("id","tenant_id","user_name","user_phone","service_id","slot_id","status","created_at","visited","telegram_id") VALUES(13,1,'Андрей','+79952714019',1,17,'confirmed','2026-10-11 12:06:10',0,NULL);
INSERT INTO "appointments" ("id","tenant_id","user_name","user_phone","service_id","slot_id","status","created_at","visited","telegram_id") VALUES(14,1,'Андрей','+79952714019',2,20,'confirmed','2026-10-11 12:16:48',0,NULL);
INSERT INTO "appointments" ("id","tenant_id","user_name","user_phone","service_id","slot_id","status","created_at","visited","telegram_id") VALUES(15,1,'Андрей','+79952714019',1,13,'confirmed','2026-10-11 12:21:21',0,NULL);
INSERT INTO "appointments" ("id","tenant_id","user_name","user_phone","service_id","slot_id","status","created_at","visited","telegram_id") VALUES(16,1,'Андрей','+79952714019',3,7,'confirmed','2026-10-11 12:34:48',0,NULL);
INSERT INTO "appointments" ("id","tenant_id","user_name","user_phone","service_id","slot_id","status","created_at","visited","telegram_id") VALUES(17,1,'Андрей','+79952714019',2,23,'cancelled','2026-10-13 03:09:04',0,'999999999');
INSERT INTO "appointments" ("id","tenant_id","user_name","user_phone","service_id","slot_id","status","created_at","visited","telegram_id") VALUES(18,1,'Андрей','+79952714019',1,21,'cancelled','2026-10-13 13:21:53',0,'999999999');
INSERT INTO "appointments" ("id","tenant_id","user_name","user_phone","service_id","slot_id","status","created_at","visited","telegram_id") VALUES(19,1,'Андрей','+79952714019',3,22,'cancelled','2026-10-13 13:40:11',0,'999999999');
CREATE TABLE schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    start_time TEXT NOT NULL DEFAULT '09:00',
    end_time TEXT NOT NULL DEFAULT '20:00',
    is_working INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    UNIQUE(tenant_id, day_of_week)
);
INSERT INTO "schedules" ("id","tenant_id","day_of_week","start_time","end_time","is_working") VALUES(1,1,0,'09:00','20:00',1);
INSERT INTO "schedules" ("id","tenant_id","day_of_week","start_time","end_time","is_working") VALUES(2,1,1,'09:00','20:00',1);
INSERT INTO "schedules" ("id","tenant_id","day_of_week","start_time","end_time","is_working") VALUES(3,1,2,'09:00','20:00',1);
INSERT INTO "schedules" ("id","tenant_id","day_of_week","start_time","end_time","is_working") VALUES(4,1,3,'09:00','20:00',1);
INSERT INTO "schedules" ("id","tenant_id","day_of_week","start_time","end_time","is_working") VALUES(5,1,4,'09:00','20:00',1);
INSERT INTO "schedules" ("id","tenant_id","day_of_week","start_time","end_time","is_working") VALUES(6,1,5,'10:00','18:00',1);
INSERT INTO "schedules" ("id","tenant_id","day_of_week","start_time","end_time","is_working") VALUES(7,1,6,'00:00','00:00',0);
DELETE FROM sqlite_sequence;
INSERT INTO "sqlite_sequence" ("name","seq") VALUES('tenants',1);
INSERT INTO "sqlite_sequence" ("name","seq") VALUES('services',5);
INSERT INTO "sqlite_sequence" ("name","seq") VALUES('slots',3431);
INSERT INTO "sqlite_sequence" ("name","seq") VALUES('appointments',19);
INSERT INTO "sqlite_sequence" ("name","seq") VALUES('schedules',7);
CREATE UNIQUE INDEX idx_slots_tenant_datetime 
ON slots(tenant_id, datetime);
CREATE INDEX idx_appointments_tenant 
ON appointments(tenant_id);
CREATE INDEX idx_appointments_status 
ON appointments(status);
CREATE INDEX idx_services_tenant 
ON services(tenant_id);
CREATE INDEX idx_slots_tenant_booked 
ON slots(tenant_id, is_booked);
CREATE INDEX idx_appointments_telegram 
ON appointments(telegram_id);