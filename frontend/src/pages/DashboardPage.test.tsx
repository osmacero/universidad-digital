import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import {
  MemoryRouter,
  Route,
  Routes,
} from 'react-router-dom'
import {
  afterEach,
  describe,
  expect,
  test,
  vi,
} from 'vitest'

import DashboardPage from './DashboardPage'

describe('DashboardPage', () => {
  afterEach(() => {
    vi.restoreAllMocks()
    localStorage.clear()
  })

  test('muestra los datos del usuario autenticado', async () => {
    localStorage.setItem(
      'access_token',
      'token-de-prueba',
    )

    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({
        email: 'usuario@universidaddigital.com',
        full_name: 'Usuario de Prueba',
        role: 'Administrador',
      }),
    } as Response)

    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <Routes>
          <Route
            path="/dashboard"
            element={<DashboardPage />}
          />
        </Routes>
      </MemoryRouter>,
    )

    expect(
      await screen.findByRole('heading', {
        name: /bienvenido, usuario de prueba/i,
      }),
    ).toBeInTheDocument()

    expect(
      screen.getByText(
        'usuario@universidaddigital.com',
      ),
    ).toBeInTheDocument()

    expect(
      screen.getByText('Administrador'),
    ).toBeInTheDocument()

    expect(fetch).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/v1/auth/me',
      expect.objectContaining({
        headers: {
          Authorization: 'Bearer token-de-prueba',
        },
      }),
    )
  })

  test('cierra la sesión y redirige al login', async () => {
    const user = userEvent.setup()

    localStorage.setItem(
      'access_token',
      'token-de-prueba',
    )

    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({
        email: 'usuario@universidaddigital.com',
        full_name: 'Usuario de Prueba',
        role: 'Administrador',
      }),
    } as Response)

    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <Routes>
          <Route
            path="/dashboard"
            element={<DashboardPage />}
          />

          <Route
            path="/login"
            element={<h1>Login de prueba</h1>}
          />
        </Routes>
      </MemoryRouter>,
    )

    await screen.findByRole('heading', {
      name: /bienvenido, usuario de prueba/i,
    })

    await user.click(
      screen.getByRole('button', {
        name: /cerrar sesión/i,
      }),
    )

    expect(
      localStorage.getItem('access_token'),
    ).toBeNull()

    expect(
      screen.getByRole('heading', {
        name: /login de prueba/i,
      }),
    ).toBeInTheDocument()
  })

  test('redirige al login cuando no existe token', async () => {
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <Routes>
          <Route
            path="/dashboard"
            element={<DashboardPage />}
          />

          <Route
            path="/login"
            element={<h1>Login sin token</h1>}
          />
        </Routes>
      </MemoryRouter>,
    )

    expect(
      await screen.findByRole('heading', {
        name: /login sin token/i,
      }),
    ).toBeInTheDocument()
  })

  test('elimina el token y redirige al login cuando auth me falla', async () => {
    localStorage.setItem(
      'access_token',
      'token-de-prueba',
    )

    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: false,
      status: 401,
    } as Response)

    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <Routes>
          <Route
            path="/dashboard"
            element={<DashboardPage />}
          />

          <Route
            path="/login"
            element={<h1>Login por sesión inválida</h1>}
          />
        </Routes>
      </MemoryRouter>,
    )

    expect(
      await screen.findByRole('heading', {
        name: /login por sesión inválida/i,
      }),
    ).toBeInTheDocument()

    expect(
      localStorage.getItem('access_token'),
    ).toBeNull()

    expect(fetch).toHaveBeenCalledTimes(1)
  })
})