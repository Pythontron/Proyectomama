import flet as ft
from login import LoginView
from navbar import NavBar
from details import DetailsView
from customer_list import CustomerListView
from facturas_view import FacturasView  # Importar la nueva vista de facturas
from database import init_db  # Importar la función para inicializar la base de datos

def main(page: ft.Page):
    page.title = "Gestor de Clientes"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Inicializar la base de datos
    init_db()

    # Función para cambiar de ruta
    def route_change(route):
        page.views.clear()
        if page.route == "/login":
            page.views.append(LoginView(page))
        elif page.route == "/details":
            page.views.append(DetailsView(page))
        elif page.route == "/customer_list":
            page.views.append(CustomerListView(page))
        elif page.route.startswith("/facturas"):
            empresa_id = int(page.route.split("=")[1])
            page.views.append(FacturasView(page, empresa_id))

        page.update()

    # Asignar la función de cambio de ruta
    page.on_route_change = route_change

    # Ir directamente a la página principal al iniciar
    page.go("/details")

ft.app(target=main)
