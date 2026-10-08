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