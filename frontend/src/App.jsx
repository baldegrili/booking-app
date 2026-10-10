import { useEffect, useState } from 'react'
import { DayPicker } from 'react-day-picker'
import 'react-day-picker/dist/style.css'
import { getServices, getSlots, bookAppointment, getTenant, getRole, getAppointments, addService, getSlotsByDate } from './api'
import './App.css'

export default function App() {
  const [tenant, setTenant] = useState(null)
  const [role, setRole] = useState(null)
  const [screen, setScreen] = useState('home')
  const [testId, setTestId] = useState(null)

  const [services, setServices] = useState([])
  const [appointments, setAppointments] = useState([])
  const [selectedService, setSelectedService] = useState(null)
  const [selectedDate, setSelectedDate] = useState(null)
  const [slots, setSlots] = useState([])
  const [selectedSlot, setSelectedSlot] = useState(null)
  const [name, setName] = useState('')
  const [phone, setPhone] = useState('')
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(false)

  const [newService, setNewService] = useState({ name: '', price: '', description: '' })
  const [showAddForm, setShowAddForm] = useState(false)

  // Получение ID из Telegram
  useEffect(() => {
    const tg = window.Telegram?.WebApp
    const userId = tg?.initDataUnsafe?.user?.id
    if (userId) {
      setTestId(userId)
    } else {
      setTestId(507233401)
    }
  }, [])

  // Загрузка данных при старте
  useEffect(() => {
    if (!testId) return
    getTenant().then(setTenant)
    getServices().then(setServices)
    getRole(testId).then(data => setRole(data.role))
  }, [testId])

  // Загрузка слотов при выборе даты
  useEffect(() => {
    if (!selectedDate) return
    const dateStr = selectedDate.toISOString().split('T')[0]
    getSlotsByDate(dateStr).then(data => {
      if (Array.isArray(data)) setSlots(data)
      else setSlots([])
    })
    setSelectedSlot(null)
  }, [selectedDate])

  // Загрузка записей для владельца
  useEffect(() => {
    if (screen === 'appointments') {
      getAppointments(testId).then(data => {
        if (Array.isArray(data)) setAppointments(data)
        else setAppointments([])
      })
    }
  }, [screen, testId])

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
        name, phone,
        service_id: selectedService.id,
        slot_id: selectedSlot.id,
      })

      if (result.success) {
        setStatus({ type: 'success', text: 'Вы успешно записаны!' })
        setSelectedSlot(null)
        setSelectedService(null)
        setSelectedDate(null)
        setSlots([])
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

  const handleAddService = async () => {
    if (!newService.name.trim() || !newService.price) {
      setStatus({ type: 'error', text: 'Заполните название и цену' })
      return
    }
    setLoading(true)
    setStatus(null)
    try {
      const result = await addService({
        name: newService.name,
        price: Number(newService.price),
        description: newService.description,
        telegram_id: String(testId),
      })
      if (result.success) {
        setStatus({ type: 'success', text: 'Услуга добавлена!' })
        const updated = await getServices()
        setServices(updated)
        setNewService({ name: '', price: '', description: '' })
        setShowAddForm(false)
      } else {
        setStatus({ type: 'error', text: result.error || 'Ошибка добавления' })
      }
    } catch (e) {
      setStatus({ type: 'error', text: 'Ошибка соединения с сервером' })
    } finally {
      setLoading(false)
    }
  }

  // --- Экран управления услугами ---
  if (screen === 'services') {
    return (
      <div className="app">
        <button className="back-button" onClick={() => setScreen('home')}>
          ← Назад
        </button>
        <h1>Управление услугами</h1>

        {!showAddForm && (
          <button className="book-button" onClick={() => setShowAddForm(true)}>
            ➕ Добавить услугу
          </button>
        )}

        {showAddForm && (
          <div className="form" style={{ marginTop: 16 }}>
            <input type="text" placeholder="Название услуги" value={newService.name} onChange={e => setNewService({ ...newService, name: e.target.value })} />
            <input type="number" placeholder="Цена, ₽" value={newService.price} onChange={e => setNewService({ ...newService, price: e.target.value })} />
            <input type="text" placeholder="Описание" value={newService.description} onChange={e => setNewService({ ...newService, description: e.target.value })} />
            <button className="book-button" onClick={handleAddService} disabled={loading}>
              {loading ? 'Сохранение...' : 'Сохранить'}
            </button>
            <button className="back-button" onClick={() => { setShowAddForm(false); setStatus(null) }}>
              Отмена
            </button>
          </div>
        )}

        {status && <div className={`status ${status.type}`}>{status.text}</div>}

        <h2>Все услуги</h2>
        <div className="list">
          {services.map(s => (
            <div key={s.id} className="card">
              <b>{s.name}</b>
              <span>{s.price} ₽</span>
            </div>
          ))}
        </div>
      </div>
    )
  }

  // --- Экран записей клиентов ---
  if (screen === 'appointments') {
    return (
      <div className="app">
        <button className="back-button" onClick={() => setScreen('home')}>
          ← Назад
        </button>
        <h1>Записи клиентов</h1>
        <div className="list">
          {appointments.length === 0 && <div className="empty">Записей пока нет</div>}
          {appointments.map((a, i) => (
            <div key={i} className="appointment-card">
              <div className="appointment-time">📅 {a.slot_datetime}</div>
              <div className="appointment-service">🔧 {a.service_name}</div>
              <div className="appointment-client">👤 {a.user_name}</div>
              <div className="appointment-phone">📞 <a href={`tel:${a.user_phone}`}>{a.user_phone}</a></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  // --- Главный экран КЛИЕНТА ---
  if (role === 'client' && screen === 'home') {
    return (
      <div className="app">
        <div className="hero">
          {tenant?.logo_url ? (
            <img src={tenant.logo_url} alt="Логотип" className="hero-logo" />
          ) : (
            <div className="hero-logo-placeholder">🔧</div>
          )}
          <h1>{tenant?.name || 'Загрузка...'}</h1>
          <p className="hero-description">{tenant?.description}</p>
        </div>

        <div className="info-block">
          {tenant?.address && (
            <div className="info-row"><span className="info-icon">📍</span><span>{tenant.address}</span></div>
          )}
          {tenant?.phone && (
            <div className="info-row"><span className="info-icon">📞</span><a href={`tel:${tenant.phone}`}>{tenant.phone}</a></div>
          )}
          {tenant?.working_hours && (
            <div className="info-row"><span className="info-icon">🕒</span><span>{tenant.working_hours}</span></div>
          )}
        </div>

        <button className="book-button" onClick={() => setScreen('booking')}>
          🔧 Записаться на услуги
        </button>
      </div>
    )
  }

  // --- Экран записи (календарь + слоты) ---
  if (screen === 'booking') {
    return (
      <div className="app">
        <button className="back-button" onClick={() => setScreen('home')}>
          ← Назад
        </button>

        <h1>Запись на услугу</h1>

        <h2>1. Выберите услугу</h2>
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

        <h2>2. Выберите дату</h2>
        <div className="calendar-wrapper">
          <DayPicker
            mode="single"
            selected={selectedDate}
            onSelect={setSelectedDate}
            locale="ru"
            disabled={{ before: new Date() }}
            weekdaysShort={['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']}
          />
        </div>

        {selectedDate && (
          <>
            <h2>3. Выберите время</h2>
            <div className="slots-grid">
              {slots.length === 0 && (
                <div className="empty">Нет свободного времени на эту дату</div>
              )}
              {slots.map(slot => (
                <div
                  key={slot.id}
                  className={`slot ${selectedSlot?.id === slot.id ? 'selected' : ''}`}
                  onClick={() => setSelectedSlot(slot)}
                >
                  {slot.datetime.split(' ')[1]}
                </div>
              ))}
            </div>
          </>
        )}

        <h2>4. Ваши данные</h2>
        <div className="form">
          <input type="text" placeholder="Имя" value={name} onChange={e => setName(e.target.value)} />
          <input type="tel" placeholder="Телефон" value={phone} onChange={e => setPhone(e.target.value)} />
        </div>

        {selectedService && selectedSlot && (
          <div className="summary">
            Вы выбрали: <b>{selectedService.name}</b> на <b>{selectedSlot.datetime}</b>
          </div>
        )}

        <button className="book-button" onClick={handleBook} disabled={loading}>
          {loading ? 'Отправка...' : 'Записаться'}
        </button>

        {status && <div className={`status ${status.type}`}>{status.text}</div>}
      </div>
    )
  }

  // --- Главный экран ВЛАДЕЛЬЦА ---
  if (role === 'owner' && screen === 'home') {
    return (
      <div className="app">
        <div className="hero">
          <div className="hero-logo-placeholder">👑</div>
          <h1>Панель владельца</h1>
          <p className="hero-description">{tenant?.name}</p>
        </div>

        <div className="admin-menu">
          <button className="admin-item" onClick={() => setScreen('services')}>
            <span className="admin-icon">🔧</span>
            <span>Управление услугами</span>
          </button>
          <button className="admin-item" onClick={() => setScreen('appointments')}>
            <span className="admin-icon">📋</span>
            <span>Записи клиентов</span>
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="app">
      <p>Загрузка...</p>
    </div>
  )
}