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

import LoginPage from './LoginPage'

describe('LoginPage', () => {
  afterEach(() => {
    vi.restoreAllMocks()
    localStorage.clear()
  })

  test('renderiza los elementos principales del formulario', () => {
    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>,
    )

    expect(
      screen.getByLabelText(/correo electrónico/i),
    ).toBeInTheDocument()

    expect(
      screen.getByLabelText(/contraseña/i),
    ).toBeInTheDocument()

    expect(
      screen.getByRole('button', { name: /ingresar/i }),
    ).toBeInTheDocument()
  })

  test('muestra un mensaje de error cuando el login falla', async () => {
    const user = userEvent.setup()

    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: false,
    } as Response)

    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>,
    )

    await user.type(
      screen.getByLabelText(/correo electrónico/i),
      'usuario@universidaddigital.com',
    )

    await user.type(
      screen.getByLabelText(/contraseña/i),
      'clave-incorrecta',
    )

    await user.click(
      screen.getByRole('button', { name: /ingresar/i }),
    )

    expect(
      await screen.findByText(
        /correo electrónico o contraseña incorrectos/i,
      ),
    ).toBeInTheDocument()

    expect(fetch).toHaveBeenCalledTimes(1)

    expect(fetch).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/v1/auth/login',
      expect.objectContaining({
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      }),
    )
  })

  test('guarda el token y redirige al dashboard cuando el login es correcto', async () => {
    const user = userEvent.setup()

    vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          access_token: 'token-de-prueba',
          token_type: 'bearer',
        }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          email: 'usuario@universidaddigital.com',
          full_name: 'Usuario de Prueba',
        }),
      } as Response)

    render(
      <MemoryRouter initialEntries={['/login']}>
        <Routes>
          <Route
            path="/login"
            element={<LoginPage />}
          />

          <Route
            path="/dashboard"
            element={<h1>Dashboard de prueba</h1>}
          />
        </Routes>
      </MemoryRouter>,
    )

    await user.type(
      screen.getByLabelText(/correo electrónico/i),
      'usuario@universidaddigital.com',
    )

    await user.type(
      screen.getByLabelText(/contraseña/i),
      'password-correcto',
    )

    await user.click(
      screen.getByRole('button', { name: /ingresar/i }),
    )

    expect(
      await screen.findByRole('heading', {
        name: /dashboard de prueba/i,
      }),
    ).toBeInTheDocument()

    expect(
      localStorage.getItem('access_token'),
    ).toBe('token-de-prueba')

    expect(fetch).toHaveBeenCalledTimes(2)

    expect(fetch).toHaveBeenNthCalledWith(
      2,
      'http://127.0.0.1:8000/api/v1/auth/me',
      expect.objectContaining({
        headers: {
          Authorization: 'Bearer token-de-prueba',
        },
      }),
    )
  })
})