import os
import sys

def ask(prompt, default=""):
    if default:
        result = input(f"{prompt} [{default}]: ").strip()
        return result if result else default
    return input(f"{prompt}: ").strip()

def main():
    print("=" * 50)
    print("  Добавление нового автосервиса")
    print("=" * 50)

    name = ask("Название автосервиса", "Мой автосервис")
    address = ask("Адрес", "г. Москва, ул. Ленина, д. 1")
    phone = ask("Телефон", "+7 (999) 123-45-67")
    description = ask("Описание", "Ремонт и обслуживание автомобилей")
    owner_id = ask("Telegram ID владельца", "")
    
    if not owner_id:
        print("ОШИБКА: Telegram ID обязателен")
        sys.exit(1)

    print("\n--- Услуги (оставьте пустым, чтобы закончить) ---")
    services = []
    while True:
        s_name = ask("Название услуги", "")
        if not s_name:
            break
        s_price = ask("Цена, ₽", "0")
        s_desc = ask("Описание услуги", "")
        services.append((s_name, int(s_price), s_desc))

    print("\n--- Генерация SQL ---")
    
    sql = []
    sql.append(f"-- Добавление тенанта: {name}")
    sql.append(f"INSERT INTO tenants (name, address, phone, description, owner_telegram_id, slot_duration, working_hours) VALUES ('{name}', '{address}', '{phone}', '{description}', '{owner_id}', 120, 'Пн–Сб: 9:00–20:00');")
    
    # Получаем ID только что созданного тенанта (последний)
    sql.append(f"-- Услуги для {name}")
    for s_name, s_price, s_desc in services:
        sql.append(f"INSERT INTO services (tenant_id, name, price, description) VALUES ((SELECT id FROM tenants WHERE name = '{name}' ORDER BY id DESC LIMIT 1), '{s_name}', {s_price}, '{s_desc}');")
    
    sql.append(f"-- График работы для {name}")
    for day in range(7):
        if day == 6:  # Воскресенье
            sql.append(f"INSERT INTO schedules (tenant_id, day_of_week, start_time, end_time, is_working) VALUES ((SELECT id FROM tenants WHERE name = '{name}' ORDER BY id DESC LIMIT 1), {day}, '00:00', '00:00', 0);")
        else:
            sql.append(f"INSERT INTO schedules (tenant_id, day_of_week, start_time, end_time, is_working) VALUES ((SELECT id FROM tenants WHERE name = '{name}' ORDER BY id DESC LIMIT 1), {day}, '09:00', '20:00', 1);")

    # Сохраняем в файл
    filename = "new_tenant.sql"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(sql))

    print(f"\n✅ Файл {filename} создан!")
    print(f"\nТеперь выполните:")
    print(f"  wrangler d1 execute booking-db --remote --file=./{filename}")
    print(f"\nПосле этого ссылка на Mini App будет:")
    print(f"  https://master.booking-frontend-7ze.pages.dev/?tenant=<ID_НОВОГО_ТЕНАНТА>")

if __name__ == "__main__":
    main()