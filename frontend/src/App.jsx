import { useEffect, useState, useRef } from 'react'
import { DayPicker } from 'react-day-picker'
import 'react-day-picker/dist/style.css'
import { getServices, getSlotsByDate, bookAppointment, getTenant, getRole, getAppointments, addService, getMyAppointments, cancelAppointment } from './api'
import './App.css'

function FadeIn({ children, delay = 0 }) {
  const ref = useRef(null)
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true)
          observer.disconnect()
        }
      },
      { threshold: 0.1 }
    )
    if (ref.current) observer.observe(ref.current)
    return () => observer.disconnect()
  }, [])

  return (
    <div ref={ref} className={`fade-in ${visible ? 'visible' : ''}`} style={{ transitionDelay: `${delay}ms` }}>
      {children}
    </div>
  )
}

function SuccessCard({ onReset }) {
  return (
    <div className="success-overlay">
      <div className="success-card">
        <div className="success-icon">✓</div>
        <h2 className="success-title">Вы записаны!</h2>
        <p className="success-text">Мы свяжемся с вами для подтверждения</p>
        <button className="book-button" onClick={onReset}>Продолжить</button>
      </div>
    </div>
  )
}

export default function App() {
  const [tenant, setTenant] = useState(null)
  const [role, setRole] = useState(null)
  const [screen, setScreen] = useState('home')
  const [testId, setTestId] = useState(null)

  const [services, setServices] = useState([])
  const [appointments, setAppointments] = useState([])
  const [myAppointments, setMyAppointments] = useState([])
  const [selectedService, setSelectedService] = useState(null)
  const [selectedDate, setSelectedDate] = useState(null)
  const [slots, setSlots] = useState([])
  const [selectedSlot, setSelectedSlot] = useState(null)
  const [name, setName] = useState('')
  const [phone, setPhone] = useState('')
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(false)

  const [openSection, setOpenSection] = useState('service')
  const [showConfirm, setShowConfirm] = useState(false)
  const [showSuccess, setShowSuccess] = useState(false)
  const [selectedAppointment, setSelectedAppointment] = useState(null)
  const [showCancelConfirm, setShowCancelConfirm] = useState(false)

  const [newService, setNewService] = useState({ name: '', price: '', description: '' })
  const [showAddForm, setShowAddForm] = useState(false)

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const urlTestId = params.get('test_id')
    const tg = window.Telegram?.WebApp
    const userId = tg?.initDataUnsafe?.user?.id
    if (userId) setTestId(userId)
    else if (urlTestId) setTestId(urlTestId)
    else setTestId(5072334101)
  }, [])

  useEffect(() => {
    if (!testId) return
    getTenant().then(setTenant)
    getServices().then(setServices)
    getRole(testId).then(data => setRole(data.role))
    getMyAppointments(testId).then(data => {
      if (Array.isArray(data)) setMyAppointments(data)
      else setMyAppointments([])
    })
  }, [testId, screen])

  useEffect(() => {
    if (!selectedDate) return
    const year = selectedDate.getFullYear()
    const month = String(selectedDate.getMonth() + 1).padStart(2, '0')
    const day = String(selectedDate.getDate()).padStart(2, '0')
    const dateStr = `${year}-${month}-${day}`

    getSlotsByDate(dateStr).then(data => {
      if (Array.isArray(data)) setSlots(data)
      else setSlots([])
    })
    setSelectedSlot(null)
  }, [selectedDate])

  useEffect(() => {
    if (screen === 'appointments') {
      getAppointments(testId).then(data => {
        if (Array.isArray(data)) setAppointments(data)
        else setAppointments([])
      })
    }
  }, [screen, testId])

  const formatDate = (date) => {
    if (!date) return ''
    return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' })
  }

  const formatDateTime = (datetime) => {
    if (!datetime) return ''
    const [datePart, timePart] = datetime.split(' ')
    const [year, month, day] = datePart.split('-')
    const date = new Date(year, month - 1, day)
    const months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
    return `${day} ${months[month - 1]}, ${timePart.slice(0, 5)}`
  }

  const isFormComplete = selectedService && selectedSlot && name.trim() && phone.trim()

  const handleBook = async () => {
    if (!isFormComplete) return
    setLoading(true)
    setStatus(null)

    try {
      const result = await bookAppointment({
        name, phone,
        service_id: selectedService.id,
        slot_id: selectedSlot.id,
        telegram_id: String(testId),
      })

      if (result.success) {
        setShowConfirm(false)
        setShowSuccess(true)
        setSelectedSlot(null)
        setSelectedService(null)
        setSelectedDate(null)
        setSlots([])
        setName('')
        setPhone('')
        setOpenSection('service')
        const updated = await getMyAppointments(testId)
        if (Array.isArray(updated)) setMyAppointments(updated)
      } else {
        setStatus({ type: 'error', text: result.error || 'Ошибка записи' })
        setShowConfirm(false)
      }
    } catch (e) {
      setStatus({ type: 'error', text: 'Ошибка соединения с сервером' })
      setShowConfirm(false)
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = async (appointmentId) => {
    setLoading(true)
    try {
      const result = await cancelAppointment(appointmentId, testId)
      if (result.success) {
        const updated = await getMyAppointments(testId)
        if (Array.isArray(updated)) setMyAppointments(updated)
        setSelectedAppointment(null)
      } else {
        setStatus({ type: 'error', text: result.error || 'Ошибка отмены' })
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

  // --- Экран "Мои записи" (клиент) ---
  if (screen === 'myAppointments') {
    return (
      <div className="app">
        <button className="back-button" onClick={() => setScreen('home')}>← Назад</button>
        <h1>Мои записи</h1>

        {myAppointments.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📋</div>
            <p>У вас пока нет записей</p>
            <button className="book-button" onClick={() => setScreen('booking')}>
              Записаться
            </button>
          </div>
        ) : (
          <div className="list">
            {myAppointments.map(a => (
              <div
                key={a.id}
                className="appointment-list-card"
                onClick={() => setSelectedAppointment(a)}
              >
                <div className="appointment-list-service">{a.service_name}</div>
                <div className="appointment-list-datetime">📅 {formatDateTime(a.slot_datetime)}</div>
                <div className="appointment-list-footer">
                  <span className="appointment-list-price">💰 {a.service_price} ₽</span>
                  <span className="appointment-list-arrow">▸</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {selectedAppointment && (
          <div className="modal-overlay" onClick={() => setSelectedAppointment(null)}>
            <div className="modal" onClick={e => e.stopPropagation()}>
              <h2>Запись</h2>
              <div className="modal-info">
                <div className="modal-row">
                  <span>🔧 Услуга</span>
                  <b>{selectedAppointment.service_name}</b>
                </div>
                <div className="modal-row">
                  <span>💰 Цена</span>
                  <b>{selectedAppointment.service_price} ₽</b>
                </div>
                <div className="modal-row">
                  <span>📅 Дата и время</span>
                  <b>{formatDateTime(selectedAppointment.slot_datetime)}</b>
                </div>
                <div className="modal-row">
                  <span>👤 Имя</span>
                  <b>{selectedAppointment.user_name}</b>
                </div>
                <div className="modal-row">
                  <span>📞 Телефон</span>
                  <b>{selectedAppointment.user_phone}</b>
                </div>
              </div>
              <button
                className="cancel-button"
                onClick={() => setShowCancelConfirm(true)}
                disabled={loading}
              >
                Отменить запись
              </button>
              <button className="back-button" style={{ textAlign: 'center', width: '100%', marginTop: 10 }} onClick={() => setSelectedAppointment(null)}>
                Закрыть
              </button>
            </div>
          </div>
        )}
        {showCancelConfirm && selectedAppointment && (
          <div className="modal-overlay" onClick={() => setShowCancelConfirm(false)}>
            <div className="modal" onClick={e => e.stopPropagation()}>
              <h2>Отменить запись?</h2>
              <div className="modal-info">
                <div className="modal-row">
                  <span>🔧 Услуга</span>
                  <b>{selectedAppointment.service_name}</b>
                </div>
                <div className="modal-row">
                  <span>📅 Дата и время</span>
                  <b>{formatDateTime(selectedAppointment.slot_datetime)}</b>
                </div>
              </div>
              <p style={{ color: '#888', fontSize: 14, marginBottom: 20, textAlign: 'center' }}>
                Это действие нельзя отменить
              </p>
              <button
                className="cancel-button"
                onClick={() => {
                  handleCancel(selectedAppointment.id)
                  setShowCancelConfirm(false)
                }}
                disabled={loading}
              >
                {loading ? 'Отмена...' : 'Да, отменить'}
              </button>
              <button
                className="back-button"
                style={{ textAlign: 'center', width: '100%', marginTop: 10 }}
                onClick={() => setShowCancelConfirm(false)}
              >
                Нет, оставить
              </button>
            </div>
          </div>
        )}
      </div>
    )
  }

  // --- Управление услугами (владелец) ---
  if (screen === 'services') {
    return (
      <div className="app">
        <button className="back-button" onClick={() => setScreen('home')}>← Назад</button>
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
            <button className="cancel-button" onClick={() => { setShowAddForm(false); setStatus(null) }}>
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

  // --- Записи клиентов (владелец) ---
  if (screen === 'appointments') {
    return (
      <div className="app">
        <button className="back-button" onClick={() => setScreen('home')}>← Назад</button>
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
        <FadeIn>
          <div className="hero">
            {tenant?.logo_url ? (
              <img src={tenant.logo_url} alt="Логотип" className="hero-logo" />
            ) : (
              <div className="hero-logo-placeholder">🔧</div>
            )}
            <h1>{tenant?.name || 'Загрузка...'}</h1>
            <p className="hero-description">{tenant?.description}</p>
          </div>
        </FadeIn>

        <FadeIn delay={100}>
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
        </FadeIn>

        <FadeIn delay={150}>
          <button className="book-button" onClick={() => setScreen('booking')}>
            🔧 Записаться на услуги
          </button>
        </FadeIn>

        <FadeIn delay={200}>
          <button className="secondary-button" onClick={() => setScreen('myAppointments')}>
            📋 Мои записи {myAppointments.length > 0 && `(${myAppointments.length})`}
          </button>
        </FadeIn>

        {status && <div className={`status ${status.type}`}>{status.text}</div>}
      </div>
    )
  }

  // --- Экран записи (ВИЗАРД) ---
  if (screen === 'booking') {
    return (
      <div className="app">
        <button className="back-button" onClick={() => setScreen('home')}>← Назад</button>
        <h1>Запись в студию</h1>

        <div className={`wizard-step ${selectedService ? 'done' : ''} ${openSection === 'service' ? 'open' : ''}`}>
          <div className="wizard-header" onClick={() => setOpenSection(openSection === 'service' ? null : 'service')}>
            <div className="wizard-step-number">{selectedService ? '✓' : '1'}</div>
            <div className="wizard-header-content">
              {selectedService ? (
                <>
                  <div className="wizard-label">Услуга</div>
                  <div className="wizard-value">{selectedService.name} — {selectedService.price} ₽</div>
                </>
              ) : (
                <div className="wizard-label">Выбрать услугу</div>
              )}
            </div>
            <span className="wizard-arrow">{selectedService ? '✎' : '▸'}</span>
          </div>

          {openSection === 'service' && (
            <div className="wizard-body">
              {services.map(s => (
                <div key={s.id} className="card" onClick={() => { setSelectedService(s); setOpenSection('date') }}>
                  <b>{s.name}</b>
                  <span>{s.price} ₽</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className={`wizard-step ${selectedSlot ? 'done' : ''} ${openSection === 'date' ? 'open' : ''}`}>
          <div className="wizard-header" onClick={() => selectedService && setOpenSection(openSection === 'date' ? null : 'date')}>
            <div className="wizard-step-number">{selectedSlot ? '✓' : '2'}</div>
            <div className="wizard-header-content">
              {selectedSlot ? (
                <>
                  <div className="wizard-label">Дата и время</div>
                  <div className="wizard-value">{formatDate(selectedDate)}, {selectedSlot.datetime.split(' ')[1]}</div>
                </>
              ) : (
                <div className="wizard-label">Выбрать дату</div>
              )}
            </div>
            <span className="wizard-arrow">{selectedSlot ? '✎' : '▸'}</span>
          </div>

          {openSection === 'date' && (
            <div className="wizard-body">
              <div className="calendar-wrapper">
                <DayPicker
                  mode="single"
                  selected={selectedDate}
                  onSelect={setSelectedDate}
                  disabled={{ before: new Date() }}
                  weekdaysShort={['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']}
                />
              </div>

              {selectedDate && (
                <>
                  <div className="wizard-subtitle">Свободное время</div>
                  <div className="slots-grid">
                    {slots.length === 0 && <div className="empty">Нет свободного времени</div>}
                    {slots.map(slot => (
                      <div
                        key={slot.id}
                        className={`slot ${selectedSlot?.id === slot.id ? 'selected' : ''}`}
                        onClick={() => { setSelectedSlot(slot); setOpenSection('contacts') }}
                      >
                        {slot.datetime.split(' ')[1]}
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          )}
        </div>

        <div className={`wizard-step ${isFormComplete ? 'done' : ''} ${openSection === 'contacts' ? 'open' : ''}`}>
          <div className="wizard-header" onClick={() => selectedSlot && setOpenSection(openSection === 'contacts' ? null : 'contacts')}>
            <div className="wizard-step-number">{name && phone ? '✓' : '3'}</div>
            <div className="wizard-header-content">
              {name && phone ? (
                <>
                  <div className="wizard-label">Ваши данные</div>
                  <div className="wizard-value">{name}, {phone}</div>
                </>
              ) : (
                <div className="wizard-label">Ваши данные</div>
              )}
            </div>
            <span className="wizard-arrow">{name && phone ? '✎' : '▸'}</span>
          </div>

          {openSection === 'contacts' && (
            <div className="wizard-body">
              <div className="form">
                <input type="text" placeholder="Имя" value={name} onChange={e => setName(e.target.value)} />
                <input type="tel" placeholder="Телефон" value={phone} onChange={e => setPhone(e.target.value)} />
              </div>
            </div>
          )}
        </div>

        <button className="book-button" onClick={() => setShowConfirm(true)} disabled={!isFormComplete || loading}>
          Записаться
        </button>

        {status && <div className={`status ${status.type}`}>{status.text}</div>}

        {showConfirm && (
          <div className="modal-overlay" onClick={() => setShowConfirm(false)}>
            <div className="modal" onClick={e => e.stopPropagation()}>
              <h2>Подтвердите запись</h2>
              <div className="modal-info">
                <div className="modal-row"><span>🔧 Услуга</span><b>{selectedService.name}</b></div>
                <div className="modal-row"><span>💰 Цена</span><b>{selectedService.price} ₽</b></div>
                <div className="modal-row"><span>📅 Дата и время</span><b>{formatDate(selectedDate)}, {selectedSlot.datetime.split(' ')[1]}</b></div>
                <div className="modal-row"><span>👤 Имя</span><b>{name}</b></div>
                <div className="modal-row"><span>📞 Телефон</span><b>{phone}</b></div>
              </div>
              <button className="book-button" onClick={handleBook} disabled={loading}>
                {loading ? 'Отправка...' : 'Подтвердить'}
              </button>
              <button className="cancel-button" onClick={() => setShowConfirm(false)}>Отмена</button>
            </div>
          </div>
        )}

        {showSuccess && <SuccessCard onReset={() => { setShowSuccess(false); setScreen('myAppointments') }} />}
      </div>
    )
  }

  // --- Главный экран ВЛАДЕЛЬЦА ---
  if (role === 'owner' && screen === 'home') {
    return (
      <div className="app">
        <FadeIn>
          <div className="hero">
            <div className="hero-logo-placeholder">👑</div>
            <h1>Панель владельца</h1>
            <p className="hero-description">{tenant?.name}</p>
          </div>
        </FadeIn>

        <FadeIn delay={100}>
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
        </FadeIn>
      </div>
    )
  }

  return (
    <div className="app">
      <p>Загрузка...</p>
    </div>
  )
}