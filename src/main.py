import tkinter as tk
from tkinter import ttk, messagebox
import csv
from datetime import datetime

class TicketManager:
    def __init__(self, csv_file='tickets.csv'):
        # Archivo donde se almacenan los tickets
        self.csv_file = csv_file
        self.tickets = []
        self.cargar_tickets()

    def cargar_tickets(self):
        """
        Carga los tickets existentes desde un archivo CSV.
        Si el archivo no existe, inicializa la lista vacía.
        """
        try:
            with open(self.csv_file, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.tickets = list(reader)
        except FileNotFoundError:
            self.tickets = []  # No hay archivo previo, iniciar vacío

    def guardar_tickets(self):
        """
        Guarda la lista de tickets en el archivo CSV.
        Actualiza headers automáticamente según todas las claves de los tickets.
        """
        if not self.tickets:
            return
        # Determinar todos los campos presentes en los tickets
        all_fields = []
        for ticket in self.tickets:
            for key in ticket.keys():
                if key not in all_fields:
                    all_fields.append(key)
        # Escribir CSV con todos los campos
        with open(self.csv_file, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=all_fields)
            writer.writeheader()
            # Normalizar cada ticket para incluir todos los campos
            rows = []
            for ticket in self.tickets:
                row = {field: ticket.get(field, '') for field in all_fields}
                rows.append(row)
            writer.writerows(rows)

    def classify_ticket(self, description):
        """
        Clasifica automáticamente un ticket según palabras clave en la descripción.
        """
        desc = description.lower()
        if any(k in desc for k in ['fuga', 'inundación', 'desborde']):
            return 'agua'
        if any(k in desc for k in ['apagón', 'corte', 'cable']):
            return 'electricidad'
        if any(k in desc for k in ['robo', 'asalto', 'vandalismo']):
            return 'seguridad'
        if any(k in desc for k in ['ruido', 'fiesta', 'música']):
            return 'ruido'
        if any(k in desc for k in ['basura', 'desorden', 'limpieza']):
            return 'limpieza'
        return 'otro'

    def prioritize_ticket(self, category):
        """
        Asigna prioridad según la categoría del ticket.
        """
        if category in ('seguridad', 'electricidad'):
            return 'Alta'
        if category == 'agua':
            return 'Media'
        if category in ('ruido', 'limpieza'):
            return 'Baja'
        return 'Media'

    def crear_ticket(self):
        """
        Abre una ventana para ingresar un nuevo ticket.
        Clasifica y prioriza automáticamente antes de guardar.
        """
        ventana = tk.Toplevel(self.root)
        ventana.title("Nuevo Ticket")

        # Campos de entrada
        tk.Label(ventana, text="Nombre del residente:").grid(row=0, column=0, padx=5, pady=5)
        nombre_entry = tk.Entry(ventana)
        nombre_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(ventana, text="Descripción:").grid(row=1, column=0, padx=5, pady=5)
        desc_text = tk.Text(ventana, width=40, height=5)
        desc_text.grid(row=1, column=1, padx=5, pady=5)

        def guardar():
            # Recolecta datos, clasifica y prioriza
            nombre = nombre_entry.get().strip()
            descripcion = desc_text.get('1.0', 'end').strip()
            if not nombre or not descripcion:
                messagebox.showwarning("Campos vacíos", "Por favor, ingresa nombre y descripción.")
                return
            categoria = self.classify_ticket(descripcion)
            prioridad = self.prioritize_ticket(categoria)
            ticket = {
                'nombre': nombre,
                'categoria': categoria,
                'prioridad': prioridad,
                'descripcion': descripcion,
                'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'estado': 'Pendiente'
            }
            self.tickets.append(ticket)
            self.guardar_tickets()
            messagebox.showinfo(
                "Éxito", f"Ticket creado. Categoría: {categoria}, Prioridad: {prioridad}."
            )
            ventana.destroy()

        tk.Button(ventana, text="Guardar", command=guardar).grid(
            row=2, column=0, columnspan=2, pady=10
        )

    def ver_historial(self):
        """
        Muestra una ventana con todos los tickets, incluyendo prioridad.
        """
        ventana = tk.Toplevel(self.root)
        ventana.title("Historial de Tickets")

        cols = ['nombre', 'categoria', 'prioridad', 'descripcion', 'fecha', 'estado']
        tree = ttk.Treeview(ventana, columns=cols, show='headings')
        for col in cols:
            tree.heading(col, text=col.capitalize())
            tree.column(col, width=100)
        tree.pack(fill=tk.BOTH, expand=True)

        for t in self.tickets:
            tree.insert('', tk.END, values=[t.get(c, '') for c in cols])

    def generar_reporte(self):
        """
        Muestra estadísticas de tickets por categoría y prioridad.
        """
        total = len(self.tickets)
        if total == 0:
            messagebox.showwarning("Sin datos", "No hay tickets para generar reporte.")
            return

        # Cuenta tickets por categoría y prioridad
        stats_cat = {}
        stats_prio = {}
        for t in self.tickets:
            stats_cat[t['categoria']] = stats_cat.get(t['categoria'], 0) + 1
            stats_prio[t['prioridad']] = stats_prio.get(t['prioridad'], 0) + 1

        reporte = f"Total de tickets: {total}\n\n"
        reporte += "Tickets por categoría:\n"
        for cat, cnt in stats_cat.items():
            reporte += f"- {cat}: {cnt}\n"
        reporte += "\nTickets por prioridad:\n"
        for pr, cnt in stats_prio.items():
            reporte += f"- {pr}: {cnt}\n"

        messagebox.showinfo("Reporte", reporte)

    def setup_ui(self):
        """
        Configura la ventana principal y el menú.
        """
        self.root = tk.Tk()
        self.root.title("Agente de Gestión de Tickets")
        self.root.geometry('600x400')

        menubar = tk.Menu(self.root)

        ticket_menu = tk.Menu(menubar, tearoff=0)
        ticket_menu.add_command(label="Nuevo Ticket", command=self.crear_ticket)
        ticket_menu.add_command(label="Historial", command=self.ver_historial)
        ticket_menu.add_separator()
        ticket_menu.add_command(label="Salir", command=self.root.quit)
        menubar.add_cascade(label="Tickets", menu=ticket_menu)

        report_menu = tk.Menu(menubar, tearoff=0)
        report_menu.add_command(label="Generar Reporte", command=self.generar_reporte)
        menubar.add_cascade(label="Reportes", menu=report_menu)

        self.root.config(menu=menubar)

    def run(self):
        """
        Inicia la aplicación.
        """
        self.setup_ui()
        self.root.mainloop()

if __name__ == "__main__":
    manager = TicketManager()
    manager.run()
