import flet as ft
from navbar import NavBar
from database import get_connection
from datetime import datetime

class DetailsView(ft.View):
    def __init__(self, page):
        super().__init__(route="/details")
        self.page = page
        self.message_container = ft.Column()
        self.vendedor_id = None  # Almacenar el ID del vendedor seleccionado

        # Crear la barra de navegación
        self.appbar = NavBar(page)

        # Inicializar vista para ingresar o seleccionar vendedor
        self.show_vendedor_selection_view()

    def show_vendedor_selection_view(self):
        self.controls.clear()
        self.message_container.controls.clear()

        self.vendedor_nombre = ft.TextField(label="Nombre del Vendedor", width=360, height=45)
        self.save_vendedor_button = ft.ElevatedButton(text="Guardar Vendedor", on_click=self.on_save_vendedor_click)

        # Crear el dropdown para seleccionar un vendedor existente
        self.vendedores_dropdown = ft.Dropdown(
            width=360,
            options=self.get_vendedores_options(),
            on_change=self.on_select_vendedor
        )

        self.controls.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Seleccione o ingrese el nombre del vendedor", style=ft.TextStyle(size=24, weight=ft.FontWeight.BOLD)),
                        self.vendedores_dropdown,
                        ft.Text("O ingrese un nuevo vendedor"),
                        self.vendedor_nombre,
                        self.save_vendedor_button,
                        self.message_container  # Añadir contenedor de mensajes
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                alignment=ft.alignment.center,
            )
        )

        self.page.update()

    def get_vendedores_options(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, nombre FROM vendedores')
        rows = cursor.fetchall()
        conn.close()
        return [ft.dropdown.Option(key=row[0], text=row[1]) for row in rows]

    def on_save_vendedor_click(self, e):
        vendedor_nombre = self.vendedor_nombre.value

        # Limpiar mensajes anteriores
        self.message_container.controls.clear()

        # Validar que el campo esté lleno
        if not vendedor_nombre:
            self.message_container.controls.append(ft.Text("Debe ingresar el nombre del vendedor", color=ft.colors.RED))
            self.page.update()
            return

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO vendedores (nombre)
            VALUES (?)
        ''', (vendedor_nombre,))

        self.vendedor_id = cursor.lastrowid

        conn.commit()
        conn.close()

        # Mostrar los campos de detalles
        self.show_details_view()

    def on_select_vendedor(self, e):
        self.vendedor_id = e.control.value
        self.show_details_view()

    def show_details_view(self):
        self.controls.clear()
        self.message_container.controls.clear()

        # Crear los controles de la vista de detalles
        self.nombre = ft.TextField(label="Nombre de la Empresa", width=360, height=45)
        self.razon_social = ft.TextField(label="Razón Social", width=360, height=45)
        self.numero_cliente = ft.TextField(label="Número de Cliente", width=360, height=45)
        self.rut = ft.TextField(label="RUT", width=360, height=45)
        self.direccion = ft.TextField(label="Dirección", width=360, height=45)
        self.telefono = ft.TextField(label="Teléfono", width=360, height=45, keyboard_type=ft.KeyboardType.NUMBER)
        self.save_button = ft.ElevatedButton(text="Guardar Empresa", on_click=self.on_save_details_click)

        self.controls.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Ingrese los detalles de la empresa", style=ft.TextStyle(size=24, weight=ft.FontWeight.BOLD)),
                        self.nombre,
                        self.razon_social,
                        self.numero_cliente,
                        self.rut,
                        self.direccion,
                        self.telefono,
                        self.save_button,
                        self.message_container  # Añadir contenedor de mensajes
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                alignment=ft.alignment.center,
            )
        )

        self.page.update()

    def on_save_details_click(self, e):
        nombre = self.nombre.value
        razon_social = self.razon_social.value
        numero_cliente = self.numero_cliente.value
        rut = self.rut.value
        direccion = self.direccion.value
        telefono = self.telefono.value
        
        # Limpiar mensajes anteriores
        self.message_container.controls.clear()

        # Validar que todos los campos estén llenos
        if not all([nombre, razon_social, numero_cliente, rut, direccion, telefono]):
            self.message_container.controls.append(ft.Text("Debe ingresar toda la información", color=ft.colors.RED))
            self.page.update()
            return

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO empresas (vendedor_id, nombre, razon_social, numero_cliente, RUT, direccion, telefono)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (self.vendedor_id, nombre, razon_social, numero_cliente, rut, direccion, telefono))

        conn.commit()
        conn.close()

        self.message_container.controls.append(ft.Text("Empresa guardada exitosamente!", color=ft.colors.GREEN))
        self.page.update()
