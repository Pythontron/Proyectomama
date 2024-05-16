import flet as ft

class LoginView(ft.View):
    def __init__(self, page):
        super().__init__(route="/login")
        self.page = page
        self.message_container = ft.Column()

        # Crear los controles de la vista de login
        self.username_input = ft.TextField(label="Usuario", width=360)
        self.password_input = ft.TextField(label="Contraseña", password=True, width=360, on_submit=self.on_login_submit,can_reveal_password=True)
        self.login_button = ft.ElevatedButton(text="Entrar", on_click=self.on_login_click)

        # Añadir los controles a la vista
        self.controls.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Ingresa tu usuario y contraseña", style=ft.TextStyle(size=24, weight=ft.FontWeight.BOLD)),
                        self.username_input,
                        self.password_input,
                        self.login_button,
                        self.message_container  # Añadir contenedor de mensajes
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                alignment=ft.alignment.center,
                padding=180
                
            )
        )

    def on_login_click(self, e):
        self.authenticate()
    
    def on_login_submit(self,e):
        self.authenticate()
    
    def authenticate(self):
        username = self.username_input.value
        password = self.password_input.value

        # Limpiar mensajes anteriores
        self.message_container.controls.clear()

        # Aquí puedes agregar la lógica de autenticación
        if username == "admin" and password == "pass":
            self.message_container.controls.append(ft.Text("Login exitoso!", color=ft.colors.GREEN))
            self.page.go("/details")
        else:
            self.message_container.controls.append(ft.Text("Fallo de login. Inténtalo de nuevo.", color=ft.colors.RED))

        # Actualizar la página para reflejar los cambios
        self.page.update()