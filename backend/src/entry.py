from workers import WorkerEntrypoint, Response, fetch, Request
import json
import hashlib
import hmac
import time
from urllib.parse import parse_qsl, unquote

def validate_init_data(init_data: str, bot_token: str, expires_in: int = 86400) -> dict | None:
    """
    Проверяет подпись initData от Telegram.
    Возвращает распарсенные данные, если подпись верна, иначе None.
    """
    try:
        # Парсим строку initData
        parsed = dict(parse_qsl(init_data, keep_blank_values=True))
        
        # Извлекаем хэш
        received_hash = parsed.pop("hash", None)
        if not received_hash:
            return None
        
        # Проверяем срок действия (auth_date)
        auth_date = int(parsed.get("auth_date", 0))
        if expires_in > 0 and (time.time() - auth_date) > expires_in:
            return None  # Данные просрочены
        
        # Формируем строку для проверки: сортируем ключи и склеиваем
        data_check_string = "\n".join(
            f"{key}={value}" for key, value in sorted(parsed.items())
        )
        
        # Вычисляем секретный ключ
        secret_key = hmac.new(
            b"WebAppData",
            bot_token.encode(),
            hashlib.sha256
        ).digest()
        
        # Вычисляем хэш
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Сравниваем
        if not hmac.compare_digest(calculated_hash, received_hash):
            return None
        
        # Парсим user (если есть)
        if "user" in parsed:
            parsed["user"] = json.loads(parsed["user"])
        
        return parsed
    
    except Exception as e:
        print(f"DEBUG: initData validation error: {e}")
        return None

class Default(WorkerEntrypoint):
    def get_tenant_id(self, request_url, body=None):
        # Из тела (для POST/PUT)
        if body and body.get("tenant_id"):
            return int(body["tenant_id"])
            
        # Из URL (для GET)
        if "tenant_id=" in request_url:
            try:
                return int(request_url.split("tenant_id=")[1].split("&")[0])
            except:
                pass
            
        # Fallback
        return 1
    async def fetch(self, request):
        url = str(request.url)
        path = url.split("?")[0]
        tenant_id = self.get_tenant_id(url)
        print(f"DEBUG: method={request.method}, path={path}")
        
        # CORS-заголовки для фронтенда (Mini App)
        # Разрешённые источники (Origin)
        allowed_origins = [
            "https://master.booking-frontend-7ze.pages.dev",
            "https://web.telegram.org",
            "https://telegram.org",
        ]
        
        # Получаем Origin из запроса
        origin = request.headers.get("Origin", "")
        
        # Если Origin в списке разрешённых — подставляем его
        if origin in allowed_origins:
            allow_origin = origin
        else:
            # Fallback для Telegram WebView (может не присылать Origin)
            allow_origin = "https://master.booking-frontend-7ze.pages.dev"
        
        headers = {
            "Access-Control-Allow-Origin": allow_origin,
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "86400",  # Кэшируем preflight на 24 часа
        }
        
        # Preflight-запрос от браузера
        if request.method == "OPTIONS":
            return Response("", headers=headers)
        
        if path.endswith("/api/whoami"):
            parts = url.split("?")
            query = parts[1] if len(parts) > 1 else ""
            
            # Пытаемся получить initData из query
            init_data = None
            if "initData=" in query:
                init_data = unquote(query.split("initData=")[1].split("&")[0])
            
            # Если initData есть — проверяем подпись
            if init_data:
                # Получаем токен бота тенанта
                tenant_id = self.get_tenant_id(url)
                tenant = await self.env.booking_db.prepare(
                    "SELECT telegram_bot_token FROM tenants WHERE id = ?"
                ).bind(tenant_id).first()
                
                if tenant and tenant["telegram_bot_token"]:
                    validated = validate_init_data(init_data, tenant["telegram_bot_token"])
                    if validated and "user" in validated:
                        telegram_id = str(validated["user"]["id"])
                    else:
                        return Response.json({"error": "Invalid initData"}, status=403, headers=headers)
                else:
                    return Response.json({"error": "Bot token not found"}, status=500, headers=headers)
            else:
                # Fallback для браузера (без initData) — используем telegram_id
                telegram_id = None
                if "telegram_id=" in query:
                    telegram_id = query.split("telegram_id=")[1].split("&")[0]
            
            if not telegram_id:
                return Response.json({"error": "Не передан telegram_id"}, status=400, headers=headers)

            check = await self.env.booking_db.prepare(
                "SELECT id FROM tenants WHERE owner_telegram_id = ?"
            ).bind(telegram_id).first()
            
            if check:
                return Response.json({"role": "owner"}, headers=headers)
            
            return Response.json({"role": "client"}, headers=headers)     # --- API для фронтенда ---
        
        if "/api/my-appointments/" in path and request.method == "DELETE":
            # Парсим appointment_id из пути
            appointment_id = path.split("/api/my-appointments/")[1].split("?")[0]
            
            # Парсим telegram_id из query
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
            
            # Проверяем, что запись принадлежит клиенту И тенанту
            tenant_id = self.get_tenant_id(url)
            check = await self.env.booking_db.prepare(
                "SELECT id, slot_id FROM appointments WHERE id = ? AND telegram_id = ? AND tenant_id = ?"
            ).bind(appointment_id, telegram_id, tenant_id).first()

            if not check:
                return Response.json(
                    {"error": "Forbidden"},
                    status=403,
                    headers=headers
                )
            
            # Отменяем запись и освобождаем слот
            await self.env.booking_db.batch([
                self.env.booking_db.prepare(
                    "UPDATE appointments SET status = 'cancelled' WHERE id = ?"
                ).bind(appointment_id),
                self.env.booking_db.prepare(
                    "UPDATE slots SET is_booked = 0 WHERE id = ?"
                ).bind(check["slot_id"]),
            ])
            # Уведомление владельцу
            info = await self.env.booking_db.prepare(
                """SELECT a.user_name, a.user_phone, s.name AS service_name, sl.datetime AS slot_datetime
                   FROM appointments a
                   JOIN services s ON s.id = a.service_id
                   JOIN slots sl ON sl.id = a.slot_id
                   WHERE a.id = ?"""
            ).bind(appointment_id).first()
            
            if info:
                owner = await self.env.booking_db.prepare(
                    "SELECT owner_telegram_id FROM tenants WHERE id = ?"
                ).bind(1).first()
                
                if owner and owner["owner_telegram_id"]:
                    message = (
                        f"❌ <b>Клиент отменил запись</b>\n\n"
                        f"👤 {info['user_name']}\n"
                        f"📞 {info['user_phone']}\n"
                        f"🔧 {info['service_name']}\n"
                        f"📅 {info['slot_datetime']}\n\n"
                        f"Слот освободился."
                    )
                    try:
                        # Получаем токен бота тенанта
                        tenant_bot = await self.env.booking_db.prepare(
                            "SELECT telegram_bot_token FROM tenants WHERE id = ?"
                        ).bind(tenant_id).first()

                        if tenant_bot and tenant_bot["telegram_bot_token"]:
                            await self.send_telegram_message_with_token(
                                owner["owner_telegram_id"], 
                                message, 
                                tenant_bot["telegram_bot_token"]
                            )
                    except Exception as e:
                        print(f"Ошибка отправки: {e}")
            
            return Response.json({"success": True}, headers=headers)

        if "/api/appointments/" in path and path.endswith("/visited") and request.method == "POST":
            appointment_id = path.split("/api/appointments/")[1].split("/visited")[0]
            
            try:
                body = await request.json()
                visited = body.get("visited")
                telegram_id = body.get("telegram_id")
                
                if not all([visited is not None, telegram_id]):
                    return Response.json(
                        {"error": "Не все поля заполнены"},
                        status=400,
                        headers=headers
                    )
                
                # Сначала узнаем, к какому тенанту относится запись
                appointment_tenant = await self.env.booking_db.prepare(
                    "SELECT tenant_id FROM appointments WHERE id = ?"
                ).bind(appointment_id).first()
                
                if not appointment_tenant:
                    return Response.json({"error": "Запись не найдена"}, status=404, headers=headers)
                
                # Проверяем, что это владелец ИМЕННО ЭТОГО тенанта
                check = await self.env.booking_db.prepare(
                    "SELECT id FROM tenants WHERE owner_telegram_id = ? AND id = ?"
                ).bind(telegram_id, appointment_tenant["tenant_id"]).first()
                
                if not check:
                    return Response.json({"error": "Forbidden"}, status=403, headers=headers)
                    
                await self.env.booking_db.prepare(
                    "UPDATE appointments SET visited = ? WHERE id = ?"
                ).bind(visited, appointment_id).run()
                
                return Response.json({"success": True}, headers=headers)
                
            except Exception as e:
                return Response.json(
                    {"error": f"Ошибка сервера: {str(e)}"},
                    status=500,
                    headers=headers
                )

        if "/api/appointments/" in path and request.method == "GET":
            # ... парсинг appointment_id и telegram_id ...
            
            # Сначала узнаем, к какому тенанту относится запись
            appointment_tenant = await self.env.booking_db.prepare(
                "SELECT tenant_id FROM appointments WHERE id = ?"
            ).bind(appointment_id).first()
            
            if not appointment_tenant:
                return Response.json({"error": "Запись не найдена"}, status=404, headers=headers)
            
            # Проверяем, что это владелец ИМЕННО ЭТОГО тенанта
            check = await self.env.booking_db.prepare(
                "SELECT id FROM tenants WHERE owner_telegram_id = ? AND id = ?"
            ).bind(telegram_id, appointment_tenant["tenant_id"]).first()
            
            if not check:
                return Response.json({"error": "Forbidden"}, status=403, headers=headers)
            
            tenant_id = appointment_tenant["tenant_id"]
            # Получаем запись
            result = await self.env.booking_db.prepare(
                """SELECT 
                    a.id,
                    a.user_name,
                    a.user_phone,
                    a.created_at,
                    a.status,
                    a.visited,
                    s.name AS service_name,
                    s.price AS service_price,
                    sl.datetime AS slot_datetime
                FROM appointments a
                JOIN services s ON s.id = a.service_id
                JOIN slots sl ON sl.id = a.slot_id
                WHERE a.id = ? AND a.tenant_id = ?
                """
            ).bind(appointment_id, tenant_id).first()
            
            if not result:
                return Response.json(
                    {"error": "Запись не найдена"},
                    status=404,
                    headers=headers
                )
            
            return Response.json(result, headers=headers)
    
        if path.endswith("/api/my-appointments"):
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
            tenant_id = self.get_tenant_id(url)
            result = await self.env.booking_db.prepare(
                """SELECT 
                    a.id,
                    a.user_name,
                    a.user_phone,
                    s.name AS service_name,
                    s.price AS service_price,
                    sl.datetime AS slot_datetime
                FROM appointments a
                JOIN services s ON s.id = a.service_id
                JOIN slots sl ON sl.id = a.slot_id
                WHERE a.telegram_id = ?
                AND a.tenant_id = ?
                AND a.status != 'cancelled'
                AND sl.datetime > datetime('now')
                ORDER BY sl.datetime"""
            ).bind(telegram_id, tenant_id).all()
            
            return Response.json(result.results, headers=headers)   

        if "/api/appointments/" in path and request.method == "DELETE":
            # ID записи из пути
            appointment_id = path.split("/api/appointments/")[1].split("?")[0]
            
            # telegram_id из query
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
            
            # Сначала узнаем, к какому тенанту относится запись
            appointment_tenant = await self.env.booking_db.prepare(
                "SELECT tenant_id FROM appointments WHERE id = ?"
            ).bind(appointment_id).first()
            
            if not appointment_tenant:
                return Response.json({"error": "Запись не найдена"}, status=404, headers=headers)
            
            # Проверяем, что это владелец ИМЕННО ЭТОГО тенанта
            check = await self.env.booking_db.prepare(
                "SELECT id FROM tenants WHERE owner_telegram_id = ? AND id = ?"
            ).bind(telegram_id, appointment_tenant["tenant_id"]).first()
            
            if not check:
                return Response.json({"error": "Forbidden"}, status=403, headers=headers)
            
            tenant_id = appointment_tenant["tenant_id"]
            
            # Получаем slot_id записи
            appointment = await self.env.booking_db.prepare(
                "SELECT slot_id FROM appointments WHERE id = ? AND tenant_id = ?"
            ).bind(appointment_id, tenant_id).first()
            
            if not appointment:
                return Response.json(
                    {"error": "Запись не найдена"},
                    status=404,
                    headers=headers
                )
            
            # Отменяем запись + освобождаем слот
            await self.env.booking_db.batch([
                self.env.booking_db.prepare(
                    "UPDATE appointments SET status = 'cancelled' WHERE id = ?"
                ).bind(appointment_id),
                self.env.booking_db.prepare(
                    "UPDATE slots SET is_booked = 0 WHERE id = ?"
                ).bind(appointment["slot_id"]),
            ])
            
            # Уведомление владельцу
            info = await self.env.booking_db.prepare(
                """SELECT a.user_name, a.user_phone, s.name AS service_name, sl.datetime AS slot_datetime
                   FROM appointments a
                   JOIN services s ON s.id = a.service_id
                   JOIN slots sl ON sl.id = a.slot_id
                   WHERE a.id = ?"""
            ).bind(appointment_id).first()
            
            if info:
                owner = await self.env.booking_db.prepare(
                    "SELECT owner_telegram_id FROM tenants WHERE id = ?"
                ).bind(tenant_id).first()
                
                if owner and owner["owner_telegram_id"]:
                    message = (
                        f"❌ <b>Запись отменена</b>\n\n"
                        f"👤 {info['user_name']}\n"
                        f"📞 {info['user_phone']}\n"
                        f"🔧 {info['service_name']}\n"
                        f"📅 {info['slot_datetime']}\n\n"
                        f"Слот освободился."
                    )
                    try:
                        # Получаем токен бота тенанта
                        tenant_bot = await self.env.booking_db.prepare(
                            "SELECT telegram_bot_token FROM tenants WHERE id = ?"
                        ).bind(tenant_id).first()

                        if tenant_bot and tenant_bot["telegram_bot_token"]:
                            await self.send_telegram_message_with_token(
                                owner["owner_telegram_id"], 
                                message, 
                                tenant_bot["telegram_bot_token"]
                            )
                    except Exception as e:
                        print(f"Ошибка отправки: {e}")
            
            return Response.json({"success": True}, headers=headers)          
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
            tenant_id = self.get_tenant_id(url)
            result = await self.env.booking_db.prepare(
                """SELECT
                    a.id,
                    a.user_name,
                    a.user_phone,
                    s.name AS service_name,
                    s.price AS service_price,
                    sl.datetime AS slot_datetime,
                    a.visited
                FROM appointments a
                JOIN services s ON s.id = a.service_id
                JOIN slots sl ON sl.id = a.slot_id
                WHERE a.tenant_id = ? AND a.status != 'cancelled'
                ORDER BY sl.datetime"""
            ).bind(tenant_id).all()
            return Response.json(result.results, headers=headers)
        if path.endswith("/api/services") and request.method == "POST":
            try:
                # 1. Читаем тело запроса
                body = await request.json()
                name = body.get("name")
                price = body.get("price")
                description = body.get("description")
                telegram_id = body.get("telegram_id")
                tenant_id = self.get_tenant_id(url, body)

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
        if "/api/services/" in path and request.method == "PUT":
            
            try:
                service_id = path.split("/api/services/")[1].split("?")[0]
                #print(f"DEBUG: PUT SERVICES triggered, service_id={service_id}")
                
                body = await request.json()
                tenant_id = self.get_tenant_id(url, body)
                telegram_id = str(body.get("telegram_id", ""))
                name = body.get("name")
                price = body.get("price")
                description = body.get("description")
                
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
                
                await self.env.booking_db.prepare(
                    "UPDATE services SET name = ?, price = ?, description = ? WHERE id = ? AND tenant_id = ?"
                ).bind(name, price, description, service_id, tenant_id).run()
                
                return Response.json({"success": True}, headers=headers)
                
            except Exception as e:
                return Response.json(
                    {"error": f"Ошибка сервера: {str(e)}"},
                    status=500,
                    headers=headers
                )
        if "/api/services/" in path and request.method == "DELETE":
            try:
                service_id = path.split("/api/services/")[1].split("?")[0]
                
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
                tenant_id = self.get_tenant_id(url)
                await self.env.booking_db.prepare(
                    "DELETE FROM services WHERE id = ? AND tenant_id = ?"
                ).bind(service_id, tenant_id).run()
                
                return Response.json({"success": True}, headers=headers)
                
            except Exception as e:
                return Response.json(
                    {"error": f"Ошибка сервера: {str(e)}"},
                    status=500,
                    headers=headers
                )        
        if path.endswith("/api/services"):
            result = await self.env.booking_db.prepare(
                "SELECT id, name, price, description FROM services WHERE tenant_id = ?"
            ).bind(tenant_id).all()
            return Response.json(result.results, headers=headers)
        if path.endswith("/api/tenant") and request.method == "PUT":
            try:
                body = await request.json()
                tenant_id = self.get_tenant_id(url, body)
                telegram_id = str(body.get("telegram_id", ""))
                
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
                
                tenant_id = 1
                
                await self.env.booking_db.prepare(
                    """UPDATE tenants SET 
                        name = ?, description = ?, address = ?, 
                        phone = ?, working_hours = ?, logo_url = ?
                       WHERE id = ?"""
                ).bind(
                    body.get("name"),
                    body.get("description"),
                    body.get("address"),
                    body.get("phone"),
                    body.get("working_hours"),
                    body.get("logo_url"),
                    tenant_id
                ).run()
                
                return Response.json({"success": True}, headers=headers)
                
            except Exception as e:
                return Response.json(
                    {"error": f"Ошибка сервера: {str(e)}"},
                    status=500,
                    headers=headers
                )
        if path.endswith("/api/schedules") and request.method == "GET":
            tenant_id = self.get_tenant_id(url)
            result = await self.env.booking_db.prepare(
                "SELECT day_of_week, start_time, end_time, is_working FROM schedules WHERE tenant_id = ? ORDER BY day_of_week"
            ).bind(tenant_id).all()
            tenant = await self.env.booking_db.prepare(
                "SELECT slot_duration FROM tenants WHERE id = 1"
            ).first()
            return Response.json({
                "schedules": result.results,
                "slot_duration": tenant["slot_duration"] if tenant else 120
            }, headers=headers)
        if path.endswith("/api/schedules") and request.method == "PUT":
            try:
                body = await request.json()
                tenant_id = self.get_tenant_id(url, body)
                telegram_id = str(body.get("telegram_id", ""))
                
                if not telegram_id:
                    return Response.json({"error": "Не передан telegram_id"}, status=401, headers=headers)
                
                check = await self.env.booking_db.prepare(
                    "SELECT id FROM tenants WHERE owner_telegram_id = ?"
                ).bind(telegram_id).first()
                
                if not check:
                    return Response.json({"error": "Forbidden"}, status=403, headers=headers)
                
                schedules = body.get("schedules", [])
                slot_duration = body.get("slot_duration")
                
                if slot_duration:
                    await self.env.booking_db.prepare(
                        "UPDATE tenants SET slot_duration = ? WHERE id = 1"
                    ).bind(slot_duration).run()
                
                for s in schedules:
                    await self.env.booking_db.prepare(
                        """UPDATE schedules SET start_time = ?, end_time = ?, is_working = ? 
                           WHERE tenant_id = 1 AND day_of_week = ?"""
                    ).bind(s["start_time"], s["end_time"], s["is_working"], s["day_of_week"]).run()
                
                await self.env.booking_db.prepare(
                    """DELETE FROM slots 
                        WHERE tenant_id = 1 
                        AND is_booked = 0 
                        AND datetime > datetime('now')
                        AND id NOT IN (SELECT slot_id FROM appointments)"""
                ).run()
                
                return Response.json({"success": True}, headers=headers)
            except Exception as e:
                return Response.json({"error": f"Ошибка: {str(e)}"}, status=500, headers=headers)        
        if path.endswith("/api/tenant") and request.method == "GET":
            result = await self.env.booking_db.prepare(
                """SELECT id, name, address, phone, working_hours, logo_url, description 
                   FROM tenants WHERE id = ?"""
            ).bind(tenant_id).first()
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
            
            await self.generate_slots(tenant_id, 30)
            result = await self.env.booking_db.prepare(
                "SELECT id, datetime FROM slots WHERE tenant_id = ? AND is_booked = 0 AND date(datetime) = ? ORDER BY datetime"
            ).bind(tenant_id, date_str).all()
            return Response.json(result.results, headers=headers)                
        if path.endswith("/api/slots"):
            await self.generate_slots(tenant_id, 30)
            result = await self.env.booking_db.prepare(
                "SELECT id, datetime FROM slots WHERE tenant_id = ? AND is_booked = 0 ORDER BY datetime"
            ).bind(tenant_id).all()
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
                telegram_id = body.get("telegram_id")
                tenant_id = self.get_tenant_id(url, body)
                
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
                        "INSERT INTO appointments (tenant_id, user_name, user_phone, service_id, slot_id, telegram_id) VALUES (?, ?, ?, ?, ?, ?)"
                    ).bind(tenant_id, user_name, user_phone, service_id, slot_id, telegram_id),
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
                        # Получаем токен бота тенанта
                        tenant_bot = await self.env.booking_db.prepare(
                            "SELECT telegram_bot_token FROM tenants WHERE id = ?"
                        ).bind(tenant_id).first()

                        if tenant_bot and tenant_bot["telegram_bot_token"]:
                            await self.send_telegram_message_with_token(
                                owner["owner_telegram_id"], 
                                message, 
                                tenant_bot["telegram_bot_token"]
                            )
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
        
        if "/webhook/telegram/" in path and request.method == "POST":
            try:
                # Достаем webhook_secret из URL (НЕ токен!)
                webhook_secret = str(path.split("/webhook/telegram/")[1])
                
                # Ищем тенанта по webhook_secret
                tenant = await self.env.booking_db.prepare(
                    "SELECT id, name, telegram_bot_token FROM tenants WHERE webhook_secret = ?"
                ).bind(webhook_secret).first()
                
                if not tenant:
                    return Response("Unknown webhook", status=404)
                
                # Проверяем заголовок от Telegram
                secret_header = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
                if secret_header != webhook_secret:
                    return Response("Forbidden", status=403)
                
                # Парсим сообщение
                body = await request.json()
                
                if "message" in body and "text" in body["message"]:
                    text = body["message"]["text"]
                    chat_id = body["message"]["chat"]["id"]
                    
                    if text == "/start":
                        mini_app_url = f"https://master.booking-frontend-7ze.pages.dev/?tenant={tenant['id']}"
                        reply_text = f"Добро пожаловать в {tenant['name']}!\nНажмите кнопку ниже, чтобы записаться."
                        
                        await self.send_telegram_message_with_button(
                            chat_id, 
                            reply_text, 
                            mini_app_url, 
                            tenant["telegram_bot_token"]
                        )
                
                return Response("OK", headers=headers)
            except Exception as e:
                print(f"ERROR webhook: {e}")
                return Response("Error", status=500)
            try:
                # Достаем токен из URL (например, /webhook/telegram/12345:ABC)
                bot_token = path.split("/webhook/telegram/")[1]
                
                # Ищем тенанта, которому принадлежит этот бот
                secret = path.split("/webhook/telegram/")[1]
                tenant = await self.env.booking_db.prepare(
                    "SELECT id, name, telegram_bot_token FROM tenants WHERE webhook_secret = ?"
                ).bind(secret).first()
                
                if not tenant:
                    print(f"DEBUG: Неизвестный токен бота: {bot_token[:10]}...")
                    return Response("Unknown bot", status=404)

                # Парсим сообщение от Telegram
                body = await request.json()
                
                # Проверяем, есть ли сообщение и команда /start
                if "message" in body and "text" in body["message"]:
                    text = body["message"]["text"]
                    chat_id = body["message"]["chat"]["id"]
                    
                    if text == "/start":
                        # Отправляем клиенту кнопку для открытия Mini App
                        # ВАЖНО: ссылка должна содержать tenant=ID
                        mini_app_url = f"https://master.booking-frontend-7ze.pages.dev/?tenant={tenant['id']}"
                        
                        reply_text = f"Добро пожаловать в {tenant['name']}!\nНажмите кнопку ниже, чтобы записаться на услугу."
                        
                        await self.send_telegram_message_with_button(chat_id, reply_text, mini_app_url, bot_token)
                
                return Response("OK", headers=headers)
            except Exception as e:
                print(f"ERROR webhook: {e}")
                return Response("Error", status=500)
        
        if "/webhook/max/" in path:
            return Response("OK: max webhook", headers=headers)
        
        # --- Корневой путь ---
        
        return Response("Booking API is running", headers=headers)

    async def send_telegram_message_with_button(self, chat_id, text, url, bot_token):
        api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        request = Request(api_url, method="POST",
            headers={"Content-Type": "application/json"},
            body=json.dumps({
                "chat_id": chat_id,
                "text": text,
                "reply_markup": {
                    "inline_keyboard": [[
                        {"text": "📅 Записаться", "web_app": {"url": url}}
                    ]]
                }
            })
        )
        try:
            await fetch(request)
        except Exception as e:
            print(f"DEBUG: fetch failed = {e}")

    async def send_telegram_message_with_token(self, chat_id, text, bot_token):
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        request = Request(url, method="POST",
            headers={"Content-Type": "application/json"},
            body=json.dumps({
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML"
            })
        )
        try:
            await fetch(request)
        except Exception as e:
            print(f"DEBUG: fetch failed = {e}")
       
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


    