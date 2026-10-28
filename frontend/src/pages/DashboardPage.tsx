import {API_URL} from '../config'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import './Dashboard.css'

interface User {
  email?: string
  full_name?: string
  name?: string
  role?: string
}

function DashboardPage() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const navigate = useNavigate()

  useEffect(() => {

    const loadUser = async () => {

      const token =
        localStorage.getItem('access_token')

      if (!token) {
        navigate('/login')
        return
      }

      try {

        const response = await fetch(
          `${API_URL}/api/v1/auth/me`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        )

        if (!response.ok) {
          throw new Error('Sesión inválida')
        }

        const data = await response.json()

        setUser(data)

      } catch {
        localStorage.removeItem('access_token')
        navigate('/login')

      } finally {
        setLoading(false)
      }
    }

    loadUser()

  }, [navigate])

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    navigate('/login')
  }

  if (loading) {
    return (
      <main className="dashboard-loading">
        Cargando Universidad Digital...
      </main>
    )
  }

  return (
    <main className="dashboard-page">

      <aside className="sidebar">

        <div className="sidebar-brand">
          <span className="dashboard-logo">
            UD
          </span>

          <div>
            <strong>Universidad</strong>
            <span>Digital</span>
          </div>
        </div>

        <nav className="dashboard-nav">
          <button className="nav-active">
            Inicio
          </button>

          <button>
            Períodos académicos
          </button>

          <button>
            Asignaturas
          </button>

          <button>
            Matrículas
          </button>

          <button>
            Calificaciones
          </button>

          <button>
            Reportes
          </button>
        </nav>

        <button
          className="logout-button"
          onClick={handleLogout}
        >
          Cerrar sesión
        </button>

      </aside>

      <section className="dashboard-content">

        <header className="dashboard-header">

          <div>
            <p>Universidad Digital</p>

            <h1>
              Bienvenido,
              {' '}
              {user?.full_name ??
               user?.name ??
               user?.email ??
               'Usuario'}
            </h1>
          </div>

          <div className="user-chip">
            <span>
              {user?.role ?? 'Usuario'}
            </span>

            <strong>
              {user?.email}
            </strong>
          </div>

        </header>

        <section className="summary-grid">

          <article className="summary-card">
            <span>Períodos</span>
            <strong>Académicos</strong>
            <p>
              Gestión de períodos académicos.
            </p>
          </article>

          <article className="summary-card">
            <span>Asignaturas</span>
            <strong>Cursos</strong>
            <p>
              Consulta y administración académica.
            </p>
          </article>

          <article className="summary-card">
            <span>Matrículas</span>
            <strong>Estudiantes</strong>
            <p>
              Administración de inscripciones.
            </p>
          </article>

          <article className="summary-card">
            <span>Notas</span>
            <strong>Calificaciones</strong>
            <p>
              Registro y consulta de resultados.
            </p>
          </article>

        </section>

        <section className="welcome-panel">

          <div>
            <span className="panel-tag">
              Sistema académico
            </span>

            <h2>
              Gestión académica centralizada
            </h2>

            <p>
              Desde este panel podrás gestionar
              asignaturas, matrículas,
              calificaciones y reportes
              académicos.
            </p>
          </div>

        </section>

      </section>

    </main>
  )
}

export default DashboardPage