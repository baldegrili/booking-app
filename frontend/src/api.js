const API_URL = 'https://booking-backend.booking-app-andrey202.workers.dev'

// Получаем tenant_id из URL (?tenant=2) или fallback на 1
export function getTenantId() {
  const params = new URLSearchParams(window.location.search)
  return params.get('tenant') || '1'
}

export async function getTenant() {
  const t = getTenantId()
  const res = await fetch(`${API_URL}/api/tenant?tenant_id=${t}`)
  return res.json()
}

export async function updateTenant(data) {
  const t = getTenantId()
  const res = await fetch(`${API_URL}/api/tenant`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ...data, tenant_id: t }),
  })
  return res.json()
}

export async function getServices() {
  const t = getTenantId()
  const res = await fetch(`${API_URL}/api/services?tenant_id=${t}`)
  return res.json()
}

export async function addService(data) {
  const t = getTenantId()
  const res = await fetch(`${API_URL}/api/services`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ...data, tenant_id: t }),
  })
  return res.json()
}

export async function updateService(id, data) {
  const t = getTenantId()
  const res = await fetch(`${API_URL}/api/services/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ...data, tenant_id: t }),
  })
  return res.json()
}

export async function deleteService(id, telegramId) {
  const t = getTenantId()
  const res = await fetch(`${API_URL}/api/services/${id}?telegram_id=${telegramId}&tenant_id=${t}`, {
    method: 'DELETE',
  })
  return res.json()
}

export async function getSlotsByDate(date) {
  const t = getTenantId()
  const res = await fetch(`${API_URL}/api/slots/by-date?date=${date}&tenant_id=${t}`)
  return res.json()
}

export async function getSlots() {
  const t = getTenantId()
  const res = await fetch(`${API_URL}/api/slots?tenant_id=${t}`)
  return res.json()
}

export async function bookAppointment(data) {
  const t = getTenantId()
  const res = await fetch(`${API_URL}/api/book`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ...data, tenant_id: t }),
  })
  return res.json()
}

export async function getRole(telegramId) {
  const t = getTenantId()
  const initData = getInitData()
  
  if (initData) {
    // Отправляем initData для проверки
    const res = await fetch(`${API_URL}/api/whoami?initData=${encodeURIComponent(initData)}&tenant_id=${t}`)
    return res.json()
  }
  
  // Fallback для браузера
  const res = await fetch(`${API_URL}/api/whoami?telegram_id=${telegramId}&tenant_id=${t}`)
  return res.json()
}

export async function getAppointments(telegramId) {
  const t = getTenantId()
  const res = await fetch(`${API_URL}/api/appointments?telegram_id=${telegramId}&tenant_id=${t}`)
  return res.json()
}

export async function getAppointmentById(id, telegramId) {
  const t = getTenantId()
  const res = await fetch(`${API_URL}/api/appointments/${id}?telegram_id=${telegramId}&tenant_id=${t}`)
  return res.json()
}

export async function markVisited(id, visited, telegramId) {
  const t = getTenantId()
  const res = await fetch(`${API_URL}/api/appointments/${id}/visited`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ visited, telegram_id: String(telegramId), tenant_id: t }),
  })
  return res.json()
}

export async function cancelAppointmentByOwner(id, telegramId) {
  const t = getTenantId()
  const res = await fetch(`${API_URL}/api/appointments/${id}?telegram_id=${telegramId}&tenant_id=${t}`, {
    method: 'DELETE',
  })
  return res.json()
}

export async function getMyAppointments(telegramId) {
  const t = getTenantId()
  const res = await fetch(`${API_URL}/api/my-appointments?telegram_id=${telegramId}&tenant_id=${t}`)
  return res.json()
}

export async function cancelAppointment(id, telegramId) {
  const t = getTenantId()
  const res = await fetch(`${API_URL}/api/my-appointments/${id}?telegram_id=${telegramId}&tenant_id=${t}`, {
    method: 'DELETE',
  })
  return res.json()
}

export async function getSchedules() {
  const t = getTenantId()
  const res = await fetch(`${API_URL}/api/schedules?tenant_id=${t}`)
  return res.json()
}

export async function updateSchedules(data) {
  const t = getTenantId()
  const res = await fetch(`${API_URL}/api/schedules`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ...data, tenant_id: t }),
  })
  return res.json()
}
export function getInitData() {
  return window.Telegram?.WebApp?.initData || ''
}