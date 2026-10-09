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