import { render, screen } from '@testing-library/react'
import {
  MemoryRouter,
  Route,
  Routes,
} from 'react-router-dom'
import { afterEach, describe, expect, test } from 'vitest'

import ProtectedRoute from './ProtectedRoute'

describe('ProtectedRoute', () => {
  afterEach(() => {
    localStorage.clear()
  })

  test('redirige al login cuando no existe token', () => {
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <Routes>
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <h1>Dashboard protegido</h1>
              </ProtectedRoute>
            }
          />
          <Route
            path="/login"
            element={<h1>Login</h1>}
          />
        </Routes>
      </MemoryRouter>,
    )

    expect(
      screen.getByRole('heading', { name: /login/i }),
    ).toBeInTheDocument()
  })

  test('permite acceder cuando existe token', () => {
    localStorage.setItem('access_token', 'token-prueba')

    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <Routes>
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <h1>Dashboard protegido</h1>
              </ProtectedRoute>
            }
          />
        </Routes>
      </MemoryRouter>,
    )

    expect(
      screen.getByRole('heading', {
        name: /dashboard protegido/i,
      }),
    ).toBeInTheDocument()
  })
})