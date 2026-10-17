describe('Universidad Digital - autenticación', () => {
  beforeEach(() => {
    cy.clearLocalStorage()
  })

  it('muestra el login correctamente', () => {
    cy.visit('/login')

    cy.contains('Iniciar sesión').should('be.visible')
    cy.get('#email').should('be.visible')
    cy.get('#password').should('be.visible')
    cy.contains('button', 'Ingresar').should('be.visible')
  })

  it('protege el dashboard cuando no existe token', () => {
    cy.visit('/dashboard')

    cy.url().should('include', '/login')
    cy.contains('Iniciar sesión').should('be.visible')
  })

  it('inicia sesión, entra al dashboard y cierra sesión correctamente', () => {
    cy.env(['E2E_EMAIL', 'E2E_PASSWORD']).then(
      ({ E2E_EMAIL, E2E_PASSWORD }) => {
        cy.visit('/login')

        cy.get('#email').type(E2E_EMAIL)
        cy.get('#password').type(E2E_PASSWORD, {
          log: false,
        })

        cy.contains('button', 'Ingresar').click()

        cy.url().should('include', '/dashboard')

        cy.contains('Cerrar sesión')
          .should('be.visible')

        cy.window().then((win) => {
          const token =
            win.localStorage.getItem('access_token')

          expect(token).to.be.a('string')
          expect(token).not.to.be.empty
        })

        cy.contains('button', 'Cerrar sesión').click()

        cy.url().should('include', '/login')

        cy.window().then((win) => {
          expect(
            win.localStorage.getItem('access_token'),
          ).to.be.null
        })

        cy.visit('/dashboard')

        cy.url().should('include', '/login')
      },
    )
  })
})