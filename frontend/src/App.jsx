import { useEffect, useState } from 'react'
import { getServices, getSlots, bookAppointment } from './api'
import './App.css'

export default function App() {
  const [services, setServices] = useState([])
  const [slots, setSlots] = useState([])
  const [selectedService, setSelectedService] = useState(null)
  const [selectedSlot, setSelectedSlot] = useState(null)
  const [name, setName] = useState('')
  const [phone, setPhone] = useState('')
  const [status, setStatus] = useState(null) // { type: 'success' | 'error', text: string }
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    getServices().then(setServices)
    getSlots().then(setSlots)
  }, [])

  const handleBook = async () => {
    if (!selectedService || !selectedSlot) {
      setStatus({ type: 'error', text: 'Выберите услугу и время' })
      return
    }
    if (!name.trim() || !phone.trim()) {
      setStatus({ type: 'error', text: 'Заполните имя и телефон' })
      return
    }

    setLoading(true)
    setStatus(null)

    try {
      const result = await bookAppointment({
        name,
        phone,
        service_id: selectedService.id,
        slot_id: selectedSlot.id,
      })

      if (result.success) {
        setStatus({ type: 'success', text: 'Вы успешно записаны!' })
        // Обновляем список слотов (занятый пропадёт)
        const updatedSlots = await getSlots()
        setSlots(updatedSlots)
        // Сбрасываем выбор
        setSelectedSlot(null)
        setSelectedService(null)
        setName('')
        setPhone('')
      } else {
        setStatus({ type: 'error', text: result.error || 'Ошибка записи' })
      }
    } catch (e) {
      setStatus({ type: 'error', text: 'Ошибка соединения с сервером' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <h1>Запись на услуги</h1>

      <h2>Выберите услугу</h2>
      <div className="list">
        {services.map(s => (
          <div
            key={s.id}
            className={`card ${selectedService?.id === s.id ? 'selected' : ''}`}
            onClick={() => setSelectedService(s)}
          >
            <b>{s.name}</b>
            <span>{s.price} ₽</span>
          </div>
        ))}
      </div>

      <h2>Выберите время</h2>
      <div className="list">
        {slots.length === 0 && <div className="empty">Нет свободных слотов</div>}
        {slots.map(slot => (
          <div
            key={slot.id}
            className={`card ${selectedSlot?.id === slot.id ? 'selected' : ''}`}
            onClick={() => setSelectedSlot(slot)}
          >
            {slot.datetime}
          </div>
        ))}
      </div>

      <h2>Ваши данные</h2>
      <div className="form">
        <input
          type="text"
          placeholder="Имя"
          value={name}
          onChange={e => setName(e.target.value)}
        />
        <input
          type="tel"
          placeholder="Телефон"
          value={phone}
          onChange={e => setPhone(e.target.value)}
        />
      </div>

      {selectedService && selectedSlot && (
        <div className="summary">
          Вы выбрали: <b>{selectedService.name}</b> на <b>{selectedSlot.datetime}</b>
        </div>
      )}

      <button
        className="book-button"
        onClick={handleBook}
        disabled={loading}
      >
        {loading ? 'Отправка...' : 'Записаться'}
      </button>

      {status && (
        <div className={`status ${status.type}`}>
          {status.text}
        </div>
      )}
    </div>
  )
}