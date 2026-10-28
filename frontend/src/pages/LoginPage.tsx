import {API_URL} from '../config'
import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import '../App.css'

function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [isError, setIsError] = useState(false)

  const navigate = useNavigate()

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    setLoading(true)
    setMessage('')
    setIsError(false)

    try {
      const loginResponse = await fetch(
        `${API_URL}/api/v1/auth/login`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email,
            password,
          }),
        }
      )

      if (!loginResponse.ok) {
        throw new Error(
          'Correo electrónico o contraseña incorrectos.'
        )
      }

      const loginData = await loginResponse.json()

      localStorage.setItem(
        'access_token',
        loginData.access_token
      )

      const meResponse = await fetch(
        `${API_URL}/api/v1/auth/me`,
        {
          headers: {
            Authorization:
              `Bearer ${loginData.access_token}`,
          },
        }
      )

      if (!meResponse.ok) {
        throw new Error(
          'No fue posible validar la sesión.'
        )
      }

      await meResponse.json()

      navigate('/dashboard')

    } catch (error) {
      localStorage.removeItem('access_token')

      setMessage(
        error instanceof Error
          ? error.message
          : 'Ocurrió un error durante el inicio de sesión.'
      )

      setIsError(true)

    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="login-page">
      <section className="login-card">

        <div className="brand-panel">
          <span className="brand-badge">UD</span>

          <h1>Universidad Digital</h1>

          <p>
            Plataforma académica para estudiantes,
            docentes y administradores.
          </p>

          <div className="brand-accent" />
        </div>

        <div className="form-panel">
          <div className="form-heading">
            <span>Bienvenido</span>

            <h2>Iniciar sesión</h2>

            <p>
              Ingresa tus credenciales para acceder
              a la plataforma.
            </p>
          </div>

          <form onSubmit={handleSubmit}>

            <label htmlFor="email">
              Correo electrónico
            </label>

            <input
              id="email"
              type="email"
              placeholder="usuario@universidaddigital.com"
              value={email}
              onChange={(event) =>
                setEmail(event.target.value)
              }
              required
            />

            <label htmlFor="password">
              Contraseña
            </label>

            <input
              id="password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(event) =>
                setPassword(event.target.value)
              }
              required
            />

            <button
              type="submit"
              disabled={loading}
            >
              {loading
                ? 'Ingresando...'
                : 'Ingresar'}
            </button>

            {message && (
              <p
                className={
                  isError
                    ? 'login-message login-error'
                    : 'login-message login-success'
                }
              >
                {message}
              </p>
            )}

          </form>

          <p className="form-footer">
            Universidad Digital · Plataforma Académica
          </p>
        </div>

      </section>
    </main>
  )
}

export default LoginPage