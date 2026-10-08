from workers import WorkerEntrypoint, Response
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
        
        # --- API для фронтенда ---
        
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
        if path.endswith("/api/slots"):
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
                    """INSERT INTO appointments 
                       (tenant_id, user_name, user_phone, service_id, slot_id) 
                       VALUES (?, ?, ?, ?, ?)"""
                ).bind(tenant_id, user_name, user_phone, service_id, slot_id),
                self.env.booking_db.prepare(
                        "UPDATE slots SET is_booked = 1 WHERE id = ?"
                ).bind(slot_id),
            ])
                
                # 6. Возвращаем успех
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