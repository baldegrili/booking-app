const API_URL = 'https://booking-backend.booking-app-andrey202.workers.dev'

export async function getServices() {
  const res = await fetch(`${API_URL}/api/services`)
  return res.json()
}

export async function getSlots() {
  const res = await fetch(`${API_URL}/api/slots`)
  return res.json()
}

export async function bookAppointment(data) {
  const res = await fetch(`${API_URL}/api/book`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  return res.json()
}

export async function getTenant() {
  const res = await fetch(`${API_URL}/api/tenant`)
  return res.json()
}

export async function getRole(telegramId) {
  const res = await fetch(`${API_URL}/api/whoami?telegram_id=${telegramId}`)
  return res.json()
}
export async function getAppointments(telegramId) {
  const res = await fetch(`${API_URL}/api/appointments?telegram_id=${telegramId}`)
  return res.json()
}
export async function addService(data) {
  const res = await fetch(`${API_URL}/api/services`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  return res.json()
}
export async function getSlotsByDate(date) {
  const res = await fetch(`${API_URL}/api/slots/by-date?date=${date}`)
  return res.json()
}
export async function getMyAppointments(telegramId) {
  const res = await fetch(`${API_URL}/api/my-appointments?telegram_id=${telegramId}`)
  return res.json()
}

export async function cancelAppointment(id, telegramId) {
  const res = await fetch(`${API_URL}/api/my-appointments/${id}?telegram_id=${telegramId}`, {
    method: 'DELETE',
  })
  return res.json()
}
export async function getAppointmentById(id, telegramId) {
  const res = await fetch(`${API_URL}/api/appointments/${id}?telegram_id=${telegramId}`)
  return res.json()
}

export async function markVisited(id, visited, telegramId) {
  const res = await fetch(`${API_URL}/api/appointments/${id}/visited`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ visited, telegram_id: String(telegramId) }),
  })
  return res.json()
}

export async function cancelAppointmentByOwner(id, telegramId) {
  const res = await fetch(`${API_URL}/api/appointments/${id}?telegram_id=${telegramId}`, {
    method: 'DELETE',
  })
  return res.json()
}
export async function updateTenant(data) {
  const res = await fetch(`${API_URL}/api/tenant`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  return res.json()
}
export async function updateService(id, data) {
  const res = await fetch(`${API_URL}/api/services/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  return res.json()
}

export async function deleteService(id, telegramId) {
  const res = await fetch(`${API_URL}/api/services/${id}?telegram_id=${telegramId}`, {
    method: 'DELETE',
  })
  return res.json()
}