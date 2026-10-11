from workers import WorkerEntrypoint, Response, fetch, Request
import json


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        url = str(request.url)
        path = url.split("?")[0]
        
        # CORS-заголовки для фронтенда (Mini App)
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        }
        
        # Preflight-запрос от браузера
        if request.method == "OPTIONS":
            return Response("", headers=headers)
        
        if path.endswith("/api/whoami"):
            parts = url.split("?")
            query = parts[1] if len(parts) > 1 else ""
            
            telegram_id = None
            if "telegram_id=" in query:
                telegram_id = query.split("telegram_id=")[1].split("&")[0]
            
            if not telegram_id:
                return Response.json(
                    {"error": "Не передан telegram_id"},
                    status=400,
                    headers=headers
                )
            
            check = await self.env.booking_db.prepare(
                "SELECT id FROM tenants WHERE owner_telegram_id = ?"
            ).bind(telegram_id).first()
            
            if check:
                return Response.json({"role": "owner"}, headers=headers)
            
            return Response.json({"role": "client"}, headers=headers)       # --- API для фронтенда ---
        
        if path.endswith("/api/appointments"):
            parts = url.split("?")
            query = parts[1] if len(parts) > 1 else ""
            
            telegram_id = None
            if "telegram_id=" in query:
                telegram_id = query.split("telegram_id=")[1].split("&")[0]
            
            if not telegram_id:
                return Response.json(
                    {"error": "Не передан telegram_id"},
                    status=401,
                    headers=headers
                )
            
            check = await self.env.booking_db.prepare(
                "SELECT id FROM tenants WHERE owner_telegram_id = ?"
            ).bind(telegram_id).first()
            
            if not check:
                return Response.json(
                    {"error": "Forbidden"},
                    status=403,
                    headers=headers
                )
            
            result = await self.env.booking_db.prepare(
                """SELECT 
                    a.user_name,
                    a.user_phone,
                    s.name AS service_name,
                    sl.datetime AS slot_datetime
                FROM appointments a
                JOIN services s ON s.id = a.service_id
                JOIN slots sl ON sl.id = a.slot_id
                WHERE a.tenant_id = ?
                ORDER BY sl.datetime"""
            ).bind(1).all()
            return Response.json(result.results, headers=headers)
        if path.endswith("/api/services") and request.method == "POST":
            try:
                # 1. Читаем тело запроса
                body = await request.json()
                name = body.get("name")
                price = body.get("price")
                description = body.get("description")
                telegram_id = body.get("telegram_id")
                tenant_id = 1

                # 2. Проверяем, что обязательные поля пришли
                if not all([name, price, telegram_id]):
                    return Response.json(
                        {"error": "Не все поля заполнены"},
                        status=400,
                        headers=headers
                    )

                # 3. Проверяем, что это владелец
                check = await self.env.booking_db.prepare(
                    "SELECT id FROM tenants WHERE owner_telegram_id = ?"
                ).bind(telegram_id).first()

                if not check:
                    return Response.json(
                        {"error": "Forbidden"},
                        status=403,
                        headers=headers
                    )

                # 4. Добавляем услугу в базу
                await self.env.booking_db.prepare(
                    "INSERT INTO services (tenant_id, name, price, description) VALUES (?, ?, ?, ?)"
                ).bind(tenant_id, name, price, description).run()

                # 5. Возвращаем успех
                return Response.json(
                    {"success": True},
                    headers=headers
                )

            except Exception as e:
                return Response.json(
                    {"error": f"Ошибка сервера: {str(e)}"},
                    status=500,
                    headers=headers
                )        
        if path.endswith("/api/services"):
            result = await self.env.booking_db.prepare(
                "SELECT id, name, price FROM services WHERE tenant_id = 1"
            ).all()
            return Response.json(result.results, headers=headers)
        if path.endswith("/api/tenant"):
            result = await self.env.booking_db.prepare(
                """SELECT id, name, address, phone, working_hours, logo_url, description 
                   FROM tenants WHERE id = 1"""
            ).first()
            return Response.json(result, headers=headers)       

        if path.endswith("/api/slots/by-date"):
            parts = url.split("?")
            query = parts[1] if len(parts) > 1 else ""
            
            date_str = None
            if "date=" in query:
                date_str = query.split("date=")[1].split("&")[0]
            
            if not date_str:
                return Response.json(
                    {"error": "Не передана дата"},
                    status=400,
                    headers=headers
                )
            
            await self.generate_slots(1, 30)
            result = await self.env.booking_db.prepare(
                "SELECT id, datetime FROM slots WHERE tenant_id = 1 AND is_booked = 0 AND date(datetime) = ? ORDER BY datetime"
            ).bind(date_str).all()
            return Response.json(result.results, headers=headers)        
        
        if path.endswith("/api/slots"):
            await self.generate_slots(1, 30)
            result = await self.env.booking_db.prepare(
                "SELECT id, datetime FROM slots WHERE tenant_id = 1 AND is_booked = 0 ORDER BY datetime"
            ).all()
            return Response.json(result.results, headers=headers)        
            # --- Создание записи ---
        
        if path.endswith("/api/book") and request.method == "POST":
            try:
                # 1. Читаем тело запроса
                body = await request.json()
                user_name = body.get("name")
                user_phone = body.get("phone")
                service_id = body.get("service_id")
                slot_id = body.get("slot_id")
                tenant_id = 1  # пока захардкожено
                
                # 2. Проверяем, что все поля пришли
                if not all([user_name, user_phone, service_id, slot_id]):
                    return Response.json(
                        {"error": "Не все поля заполнены"},
                        status=400,
                        headers=headers
                    )
                
                # 3. Проверяем, что слот ещё свободен
                slot_check = await self.env.booking_db.prepare(
                    "SELECT is_booked FROM slots WHERE id = ? AND tenant_id = ?"
                ).bind(slot_id, tenant_id).first()
                
                if not slot_check:
                    return Response.json(
                        {"error": "Слот не найден"},
                        status=404,
                        headers=headers
                    )
                
                if slot_check["is_booked"] == 1:
                    return Response.json(
                        {"error": "Это время уже занято"},
                        status=409,
                        headers=headers
                    )
                
                # 4. Создаём запись и помечаем слот — атомарно
                await self.env.booking_db.batch([
                    self.env.booking_db.prepare(
                        "INSERT INTO appointments (tenant_id, user_name, user_phone, service_id, slot_id) VALUES (?, ?, ?, ?, ?)"
                    ).bind(tenant_id, user_name, user_phone, service_id, slot_id),
                    self.env.booking_db.prepare(
                        "UPDATE slots SET is_booked = 1 WHERE id = ?"
                    ).bind(slot_id),
                ])

                # Получаем данные для уведомления
                service_info = await self.env.booking_db.prepare(
                    "SELECT name, price FROM services WHERE id = ?"
                ).bind(service_id).first()
                
                slot_info = await self.env.booking_db.prepare(
                    "SELECT datetime FROM slots WHERE id = ?"
                ).bind(slot_id).first()
                
                owner = await self.env.booking_db.prepare(
                    "SELECT owner_telegram_id FROM tenants WHERE id = ?"
                ).bind(tenant_id).first()

                # Отправляем уведомление владельцу
                if owner and owner["owner_telegram_id"]:
                    message = (
                        f"🔔 <b>Новая запись!</b>\n\n"
                        f"👤 <b>Имя:</b> {user_name}\n"
                        f"📞 <b>Телефон:</b> {user_phone}\n"
                        f"🔧 <b>Услуга:</b> {service_info['name']}\n"
                        f"💰 <b>Цена:</b> {service_info['price']} ₽\n"
                        f"📅 <b>Время:</b> {slot_info['datetime']}"
                    )
                    try:
                        await self.send_telegram_message(owner["owner_telegram_id"], message)
                    except Exception as e:
                        print(f"Ошибка отправки в Telegram: {e}")

                return Response.json(
                    {"success": True, "message": "Вы записаны!"},
                    headers=headers
                )
            
            except Exception as e:
                return Response.json(
                    {"error": f"Ошибка сервера: {str(e)}"},
                    status=500,
                    headers=headers
                )
        
        # --- Вебхуки ботов (заглушки) ---
        
        if "/webhook/telegram/" in path:
            return Response("OK: telegram webhook", headers=headers)
        
        if "/webhook/max/" in path:
            return Response("OK: max webhook", headers=headers)
        
        # --- Корневой путь ---
        
        return Response("Booking API is running", headers=headers)

    async def send_telegram_message(self, chat_id, text):
        token = self.env.TELEGRAM_BOT_TOKEN
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        request = Request(url, method="POST", 
            headers={"Content-Type": "application/json"},
            body = json.dumps({
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML"
            }
        ))
    async def generate_slots(self, tenant_id, days_ahead=30):
        from datetime import date, timedelta
        
        schedules = await self.env.booking_db.prepare(
            "SELECT day_of_week, start_time, end_time, is_working FROM schedules WHERE tenant_id = ?"
        ).bind(tenant_id).all()
        
        tenant = await self.env.booking_db.prepare(
            "SELECT slot_duration FROM tenants WHERE id = ?"
        ).bind(tenant_id).first()
        
        slot_duration = tenant["slot_duration"] or 120
        
        schedule_map = {s["day_of_week"]: s for s in schedules.results}
        
        today = date.today()
        inserts = []
        
        for i in range(days_ahead):
            current_date = today + timedelta(days=i)
            day_of_week = current_date.weekday()
            
            schedule = schedule_map.get(day_of_week)
            if not schedule or schedule["is_working"] == 0:
                continue
            
            start_h, start_m = map(int, schedule["start_time"].split(":"))
            end_h, end_m = map(int, schedule["end_time"].split(":"))
            
            current_minutes = start_h * 60 + start_m
            end_minutes = end_h * 60 + end_m
            
            while current_minutes + slot_duration <= end_minutes:
                h = current_minutes // 60
                m = current_minutes % 60
                slot_datetime = f"{current_date.isoformat()} {h:02d}:{m:02d}"
                
                inserts.append(
                    self.env.booking_db.prepare(
                        "INSERT OR IGNORE INTO slots (tenant_id, datetime, is_booked) VALUES (?, ?, 0)"
                    ).bind(tenant_id, slot_datetime)
                )
                
                current_minutes += slot_duration
        
        if inserts:
            await self.env.booking_db.batch(inserts)
    #await fetch(request)