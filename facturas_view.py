import flet as ft
from database import get_connection
from datetime import datetime
import threading

class FacturasView(ft.View):
    def __init__(self, page, empresa_id):
        super().__init__(route="/facturas")
        self.page = page
        self.empresa_id = empresa_id
        self.message_container = ft.Column()
        self.last_payment = None  # Almacenar el último pago realizado

        # Obtener el nombre de la empresa
        self.empresa_nombre = self.get_empresa_nombre(empresa_id)

        # Crear los controles de la vista de facturas
        self.numero_factura_input = ft.TextField(label="Número de Factura", width=360, height=45)
        self.deuda_input = ft.TextField(label="Cantidad de Deuda", width=360, height=45, keyboard_type=ft.KeyboardType.NUMBER)
        self.save_button = ft.ElevatedButton(text="Agregar Factura", on_click=self.on_save_factura_click)
        self.undo_button = ft.ElevatedButton(text="Deshacer Último Pago", on_click=self.on_undo_click, disabled=True)  # Botón deshacer inicialmente deshabilitado
        self.back_button = ft.ElevatedButton(text="Volver Atrás", on_click=self.on_back_click)

        # Crear la tabla de facturas
        self.facturas_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Número de Factura")),
                ft.DataColumn(ft.Text("Deuda")),
                ft.DataColumn(ft.Text("Pagado")),
                ft.DataColumn(ft.Text("Fecha")),
                ft.DataColumn(ft.Text("Fecha de Pago")),
                ft.DataColumn(ft.Text("Total")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[]
        )

        # Añadir los datos de las facturas a la vista
        self.load_facturas_data()

        # Añadir los controles a la vista
        self.controls.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(f"Gestión de Facturas para {self.empresa_nombre}", style=ft.TextStyle(size=24, weight=ft.FontWeight.BOLD)),  # Encabezado con el nombre de la empresa
                        self.numero_factura_input,
                        self.deuda_input,
                        self.save_button,
                        self.undo_button,
                        self.facturas_table,
                        self.back_button,
                        self.message_container  # Añadir contenedor de mensajes
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                ),
                alignment=ft.alignment.top_left,
                padding=20
            )
        )

    def get_empresa_nombre(self, empresa_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT nombre FROM empresas WHERE id = ?', (empresa_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else "Desconocido"

    def load_facturas_data(self):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT id, numero_factura, deuda, pagado, fecha, fecha_pago FROM facturas WHERE empresa_id = ?', (self.empresa_id,))
        rows = cursor.fetchall()

        for row in rows:
            total = row[2] - row[3]  # Calcular la diferencia entre deuda y pagado
            self.facturas_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(row[1])),  # Número de Factura
                    ft.DataCell(ft.Text(str(row[2]))),  # Deuda
                    ft.DataCell(ft.Text(str(row[3]))),  # Pagado
                    ft.DataCell(ft.Text(row[4])),  # Fecha
                    ft.DataCell(ft.Text(row[5] if row[5] else "")),  # Fecha de Pago
                    ft.DataCell(ft.Text(str(total))),  # Total
                    ft.DataCell(ft.Row([
                        ft.ElevatedButton(text="Pagar", on_click=self.create_pagar_callback(row[0]), color="Green"),
                        ft.ElevatedButton(text="Ver Pagos", on_click=self.create_ver_pagos_callback(row[0])),
                        ft.ElevatedButton(text="Eliminar", on_click=self.create_eliminar_callback(row[0]), color="Red"),
                    ])),
                ])
            )

        conn.close()
        self.page.update()

    def create_pagar_callback(self, factura_id):
        def pagar_callback(e):
            self.pagar_factura(factura_id)
        return pagar_callback

    def create_ver_pagos_callback(self, factura_id):
        def ver_pagos_callback(e):
            self.ver_pagos(factura_id)
        return ver_pagos_callback

    def create_eliminar_callback(self, factura_id):
        def eliminar_callback(e):
            self.eliminar_factura(factura_id)
        return eliminar_callback

    def pagar_factura(self, factura_id):
        pagar_input = ft.TextField(label="Cantidad a Pagar", width=360, height=45, keyboard_type=ft.KeyboardType.NUMBER)
        fecha_pago = ft.TextField(label="Fecha de Pago (YYYY-MM-DD)", value=datetime.now().strftime("%Y-%m-%d"))
        numero_factura_input = ft.TextField(label="Número de Factura", width=360, height=45)
        pagar_button = ft.ElevatedButton(text="Pagar", on_click=lambda e: self.on_pagar_click(factura_id, pagar_input, fecha_pago, numero_factura_input))

        pagar_dialog = ft.AlertDialog(
            modal=True,
            content=ft.Container(
                content=ft.Column(
                    [
                        pagar_input,
                        fecha_pago,
                        numero_factura_input
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    tight=True
                ),
                padding=10
            ),
            actions_alignment=ft.MainAxisAlignment.CENTER,
            actions=[
                pagar_button,
                ft.ElevatedButton("Cancelar", on_click=lambda e: self.close_dialog())
            ],
            on_dismiss=lambda e: self.close_dialog()
        )

        self.page.dialog = pagar_dialog
        self.page.dialog.open = True
        self.page.update()

    def on_pagar_click(self, factura_id, pagar_input, fecha_pago, numero_factura_input):
        cantidad_pagar = pagar_input.value
        fecha = fecha_pago.value
        numero_factura = numero_factura_input.value

        # Validar que los campos estén llenos y sean válidos
        if not cantidad_pagar or not numero_factura:
            self.message_container.controls.append(ft.Text("Debe ingresar la cantidad a pagar y el número de factura", color=ft.colors.RED))
            self.page.update()
            return

        try:
            cantidad_pagar = float(cantidad_pagar)
        except ValueError:
            self.message_container.controls.append(ft.Text("La cantidad debe ser un número válido", color=ft.colors.RED))
            self.page.update()
            return

        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            self.message_container.controls.append(ft.Text("La fecha debe estar en el formato YYYY-MM-DD", color=ft.colors.RED))
            self.page.update()
            return

        conn = get_connection()
        cursor = conn.cursor()

        # Registrar el pago en la tabla de pagos
        cursor.execute('''
            INSERT INTO pagos (factura_id, numero_factura, cantidad, fecha)
            VALUES (?, ?, ?, ?)
        ''', (factura_id, numero_factura, cantidad_pagar, fecha))
        
        # Actualizar la factura con el nuevo pago
        cursor.execute('UPDATE facturas SET pagado = pagado + ?, fecha_pago = ? WHERE id = ?', (cantidad_pagar, fecha, factura_id))

        conn.commit()
        conn.close()

        self.last_payment = (factura_id, cantidad_pagar)  # Almacenar el último pago realizado
        self.undo_button.disabled = False  # Habilitar el botón de deshacer
        self.page.dialog.open = False
        self.page.update()
        self.facturas_table.rows.clear()
        self.load_facturas_data()

    def ver_pagos(self, factura_id):
        conn = get_connection()
        cursor = conn.cursor()
        
        # Obtener los pagos asociados a la factura
        cursor.execute('SELECT numero_factura, cantidad, fecha FROM pagos WHERE factura_id = ?', (factura_id,))
        pagos = cursor.fetchall()
        conn.close()

        pagos_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Número de Factura")),
                ft.DataColumn(ft.Text("Cantidad")),
                ft.DataColumn(ft.Text("Fecha")),
            ],
            rows=[ft.DataRow(cells=[
                ft.DataCell(ft.Text(pago[0])),  # Número de Factura
                ft.DataCell(ft.Text(str(pago[1]))),  # Cantidad
                ft.DataCell(ft.Text(pago[2])),  # Fecha
            ]) for pago in pagos]
        )

        pagos_dialog = ft.AlertDialog(
            modal=True,
            content=ft.Container(
                content=pagos_table,
                padding=10
            ),
            actions_alignment=ft.MainAxisAlignment.CENTER,
            actions=[
                ft.ElevatedButton("Cerrar", on_click=lambda e: self.close_dialog())
            ],
            on_dismiss=lambda e: self.close_dialog()
        )

        self.page.dialog = pagos_dialog
        self.page.dialog.open = True
        self.page.update()

    def on_save_factura_click(self, e):
        numero_factura = self.numero_factura_input.value
        deuda = self.deuda_input.value

        # Limpiar mensajes anteriores
        self.message_container.controls.clear()

        # Validar que los campos estén llenos
        if not numero_factura or not deuda:
            self.message_container.controls.append(ft.Text("Debe ingresar el número de factura y la cantidad de deuda", color=ft.colors.RED))
            self.page.update()
            return

        try:
            deuda = float(deuda)
        except ValueError:
            self.message_container.controls.append(ft.Text("La cantidad debe ser un número válido", color=ft.colors.RED))
            self.page.update()
            return

        conn = get_connection()
        cursor = conn.cursor()

        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute('''
            INSERT INTO facturas (empresa_id, numero_factura, deuda, pagado, fecha)
            VALUES (?, ?, ?, 0, ?)
        ''', (self.empresa_id, numero_factura, deuda, fecha_actual))

        conn.commit()
        conn.close()

        success_message = ft.Text("Factura agregada exitosamente!", color=ft.colors.GREEN)
        self.message_container.controls.append(success_message)
        self.page.update()

        # Configurar un temporizador para ocultar el mensaje después de 2 segundos
        threading.Timer(2.0, self.clear_message, [success_message]).start()

        self.facturas_table.rows.clear()
        self.load_facturas_data()

    def clear_message(self, message):
        self.message_container.controls.remove(message)
        self.page.update()

    def close_dialog(self, e=None):
        self.page.dialog.open = False
        self.page.update()

    def on_back_click(self, e):
        self.page.go("/customer_list")

    def on_undo_click(self, e):
        if self.last_payment:
            factura_id, cantidad_pagar = self.last_payment
            conn = get_connection()
            cursor = conn.cursor()

            # Revertir el último pago en la tabla de facturas
            cursor.execute('UPDATE facturas SET pagado = pagado - ? WHERE id = ?', (cantidad_pagar, factura_id))
            
            # Eliminar el último registro de la tabla de pagos
            cursor.execute('DELETE FROM pagos WHERE id = (SELECT MAX(id) FROM pagos WHERE factura_id = ?)', (factura_id,))

            conn.commit()
            conn.close()

            self.last_payment = None  # Limpiar el último pago almacenado
            self.undo_button.disabled = True  # Deshabilitar el botón de deshacer
            self.facturas_table.rows.clear()
            self.load_facturas_data()
            self.page.update()

    def eliminar_factura(self, factura_id):
        conn = get_connection()
        cursor = conn.cursor()

        # Eliminar los registros de pagos asociados a la factura
        cursor.execute('DELETE FROM pagos WHERE factura_id = ?', (factura_id,))
        
        # Eliminar la factura
        cursor.execute('DELETE FROM facturas WHERE id = ?', (factura_id,))

        conn.commit()
        conn.close()

        self.facturas_table.rows.clear()
        self.load_facturas_data()
        self.page.update()
