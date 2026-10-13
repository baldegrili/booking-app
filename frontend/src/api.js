const API_URL = 'http://127.0.0.1:8787'

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