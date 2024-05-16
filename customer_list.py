import flet as ft
from navbar import NavBar
from database import get_connection
from facturas_view import FacturasView  # Importar la nueva vista de facturas

class CustomerListView(ft.View):
    def __init__(self, page):
        super().__init__(route="/customer_list")
        self.page = page

        # Crear la barra de navegación
        self.appbar = NavBar(page)

        # Crear los controles de la vista de la lista de empresas
        self.customer_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Vendedor")),
                ft.DataColumn(ft.Text("Nombre de la Empresa")),
                ft.DataColumn(ft.Text("Razón Social")),
                ft.DataColumn(ft.Text("Número de Cliente")),
                ft.DataColumn(ft.Text("RUT")),
                ft.DataColumn(ft.Text("Dirección")),
                ft.DataColumn(ft.Text("Teléfono")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[]
        )

        # Añadir los datos de las empresas a la vista
        self.load_customer_data()

        # Añadir los controles a la vista
        self.controls.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Lista de Empresas", style=ft.TextStyle(size=24, weight=ft.FontWeight.BOLD)),
                        self.customer_table
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                ),
                alignment=ft.alignment.top_left,
                padding=20
            )
        )

    def load_customer_data(self):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT e.id, v.nombre as vendedor_nombre, e.nombre, e.razon_social, e.numero_cliente, e.RUT, e.direccion, e.telefono
            FROM empresas e
            JOIN vendedores v ON e.vendedor_id = v.id
        ''')
        rows = cursor.fetchall()

        for row in rows:
            self.customer_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(row[1])),  # Nombre del Vendedor
                    ft.DataCell(ft.Text(row[2])),  # Nombre de la Empresa
                    ft.DataCell(ft.Text(row[3])),  # Razón Social
                    ft.DataCell(ft.Text(row[4])),  # Número de Cliente
                    ft.DataCell(ft.Text(row[5])),  # RUT
                    ft.DataCell(ft.Text(row[6])),  # Dirección
                    ft.DataCell(ft.Text(row[7])),  # Teléfono
                    ft.DataCell(ft.Row([
                        ft.ElevatedButton(text="Editar", on_click=self.create_edit_callback(row[0])),
                        ft.ElevatedButton(text="Facturas", on_click=self.create_facturas_callback(row[0]))
                    ]))
                ])
            )

        conn.close()
        self.page.update()

    def create_edit_callback(self, row_id):
        def edit_callback(e):
            self.edit_row(row_id)
        return edit_callback

    def create_facturas_callback(self, row_id):
        def facturas_callback(e):
            self.page.go(f"/facturas?empresa_id={row_id}")
        return facturas_callback

    def edit_row(self, row_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT e.id, e.nombre, e.razon_social, e.numero_cliente, e.RUT, e.direccion, e.telefono, v.nombre as vendedor_nombre
            FROM empresas e
            JOIN vendedores v ON e.vendedor_id = v.id
            WHERE e.id = ?
        ''', (row_id,))
        row = cursor.fetchone()
        conn.close()

        nombre_field = ft.TextField(label="Nombre de la Empresa", value=row[1], width=360)
        razon_social_field = ft.TextField(label="Razón Social", value=row[2], width=360)
        numero_cliente_field = ft.TextField(label="Número de Cliente", value=row[3], width=360)
        rut_field = ft.TextField(label="RUT", value=row[4], width=360)
        direccion_field = ft.TextField(label="Dirección", value=row[5], width=360)
        telefono_field = ft.TextField(label="Teléfono", value=row[6], width=360, keyboard_type=ft.KeyboardType.NUMBER)
        vendedor_nombre_field = ft.Text(value=row[7], width=360)  # Cambiar a Text ya que no requiere label

        edit_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar Empresa"),
            content=ft.Column(
                [
                    vendedor_nombre_field,
                    nombre_field,
                    razon_social_field,
                    numero_cliente_field,
                    rut_field,
                    direccion_field,
                    telefono_field
                ]
            ),
            actions=[
                ft.ElevatedButton("Guardar", on_click=lambda e: self.save_edit(e, row_id, nombre_field, razon_social_field, numero_cliente_field, rut_field, direccion_field, telefono_field)),
                ft.ElevatedButton("Cancelar", on_click=lambda e: self.close_dialog())
            ]
        )

        self.page.dialog = edit_dialog
        self.page.dialog.open = True
        self.page.update()

    def save_edit(self, e, row_id, nombre_field, razon_social_field, numero_cliente_field, rut_field, direccion_field, telefono_field):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE empresas
            SET nombre = ?, razon_social = ?, numero_cliente = ?, RUT = ?, direccion = ?, telefono = ?
            WHERE id = ?
        ''', (
            nombre_field.value,
            razon_social_field.value,
            numero_cliente_field.value,
            rut_field.value,
            direccion_field.value,
            telefono_field.value,
            row_id
        ))

        conn.commit()
        conn.close()

        self.page.dialog.open = False
        self.page.update()
        self.customer_table.rows.clear()
        self.load_customer_data()

    def close_dialog(self):
        self.page.dialog.open = False
        self.page.update()

