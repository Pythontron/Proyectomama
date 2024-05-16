import flet as ft

class NavBar(ft.AppBar):
    def __init__(self, page, title="Gestor Clientes"):
        self.page = page
        super().__init__(
            title=ft.Text(title),
            center_title=True,
            bgcolor=ft.colors.SURFACE_VARIANT,
            actions=[
                ft.Tooltip(
                    message="Agregar nuevo cliente",
                    content=ft.IconButton(ft.icons.PERSON, on_click=lambda _: page.go("/details"))
                ),
                ft.Tooltip(
                    message="Ver lista de clientes",
                    content=ft.IconButton(ft.icons.SEARCH, on_click=lambda _: page.go("/customer_list"))
                ),
                ft.Tooltip(
                    message="Cerrar sesión",
                    content=ft.IconButton(ft.icons.LOGOUT, on_click=lambda _: self.show_logout_dialog(page))
                )
            ],
        )

    def show_logout_dialog(self, page):
        def on_confirm_logout(e):
            page.dialog.open = False
            page.go("/login")
            page.update()
        
        def on_cancel_logout(e):
            page.dialog.open = False
            page.update()

        page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Advertencia"),
            content=ft.Text("¿Está seguro que desea cerrar la sesión?"),
            actions=[
                ft.ElevatedButton("Sí", on_click=on_confirm_logout),
                ft.ElevatedButton("No", on_click=on_cancel_logout),
            ],
        )
        page.dialog.open = True
        page.update()
