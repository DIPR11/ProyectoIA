import tkinter as tk
from tkinter import ttk, messagebox
import csv
from datetime import datetime

# Verificar que scikit-learn esté disponible
try:
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.preprocessing import LabelEncoder
except ImportError:
    raise ImportError("scikit-learn no está instalado. Ejecuta 'pip install scikit-learn' para usar árboles de decisión.")

class TicketManager:
    def __init__(self, csv_file='tickets.csv'):
        # Archivo donde se almacenan los tickets
        self.csv_file = csv_file
        self.tickets = []
        # Vocabulario manual ampliado para clasificación
        self.category_keywords = {
            'agua': {'fuga', 'inundación', 'desborde', 'filtración', 'derrame', 'humedad'},
            'electricidad': {'apagón', 'corte', 'cable', 'sobrecarga', 'falla eléctrica', 'cortocircuito'},
            'seguridad': {'robo', 'asalto', 'vandalismo', 'intrusión', 'allanamiento', 'violación'},
            'ruido': {'ruido', 'fiesta', 'música', 'estruendo', 'bulla', 'clamor'},
            'limpieza': {'basura', 'desorden', 'limpieza', 'residuos', 'suciedad', 'desecho'},
            'fuego': {'incendio', 'chispa', 'humo', 'llamas', 'combustión', 'alarma incendio'},
            'animales': {'perro', 'gato', 'roedor', 'avispas', 'abejas', 'mapache', 'jabalí', 'serpiente'},
            'conflictos': {'discusión', 'pelea', 'riña', 'agresión', 'confrontación', 'enfrentamiento'},
        }
        # Mapeo de prioridad por categoría
        self.priority_map = {
            'seguridad': 'Alta',
            'electricidad': 'Alta',
            'fuego': 'Alta',
            'conflictos': 'Alta',
            'agua': 'Media',
            'animales': 'Media',
            'ruido': 'Baja',
            'limpieza': 'Baja',
            'otro': 'Media'
        }
        # Preparar datos sintéticos y entrenar árboles
        self._prepare_dataset()
        self._train_classification_tree()
        self._train_priority_tree()
        # Cargar tickets existentes
        self.cargar_tickets()

    def _prepare_dataset(self):
        """
        Genera un dataset sintético a partir de category_keywords.
        Construye X (features) y y_cat, y_prio.
        """
        # Listado de todas las palabras clave como vocabulario
        self.features = sorted({kw for kws in self.category_keywords.values() for kw in kws})
        descriptions, y_cat, y_prio = [], [], []
        # Plantillas para generar oraciones
        templates = [
            "Se detecta {kw} en la instalación.",
            "Hay un reporte de {kw} hace minutos.",
            "Se percibe {kw} cerca del área común.",
            "Alerta: posible {kw} en el sector.",
        ]
        for category, kws in self.category_keywords.items():
            for kw in kws:
                for tmpl in templates:
                    desc = tmpl.format(kw=kw)
                    descriptions.append(desc)
                    y_cat.append(category)
                    y_prio.append(self.priority_map.get(category, 'Media'))
        # Construir matriz de bits (Bag of Words)
        self.X = []
        for desc in descriptions:
            vec = [1 if kw in desc.lower() else 0 for kw in self.features]
            self.X.append(vec)
        self.y_cat = y_cat
        self.y_prio = y_prio

    def _train_classification_tree(self):
        """
        Entrena el árbol de decisión para clasificar categorías.
        """
        self.le_cat = LabelEncoder()
        y = self.le_cat.fit_transform(self.y_cat)
        clf = DecisionTreeClassifier()
        clf.fit(self.X, y)
        self.clf_cat = clf

    def _train_priority_tree(self):
        """
        Entrena el árbol de decisión para predecir prioridades.
        """
        self.le_prio = LabelEncoder()
        y = self.le_prio.fit_transform(self.y_prio)
        clf = DecisionTreeClassifier()
        clf.fit(self.X, y)
        self.clf_prio = clf

    def cargar_tickets(self):
        """
        Carga los tickets existentes desde un archivo CSV.
        Si no existe, inicializa lista vacía.
        """
        try:
            with open(self.csv_file, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.tickets = list(reader)
        except FileNotFoundError:
            self.tickets = []

    def guardar_tickets(self):
        """
        Guarda la lista de tickets en el archivo CSV con todas las cabeceras.
        """
        if not self.tickets:
            return
        all_fields = []
        for ticket in self.tickets:
            for key in ticket.keys():
                if key not in all_fields:
                    all_fields.append(key)
        with open(self.csv_file, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=all_fields)
            writer.writeheader()
            rows = [{field: ticket.get(field, '') for field in all_fields}
                    for ticket in self.tickets]
            writer.writerows(rows)

    def classify_ticket(self, description):
        """
        Usa árbol de decisión entrenado para asignar categoría.
        """
        vec = [1 if kw in description.lower() else 0 for kw in self.features]
        idx = self.clf_cat.predict([vec])[0]
        return self.le_cat.inverse_transform([idx])[0]

    def prioritize_ticket(self, category, description=None):
        """
        Usa árbol de decisión entrenado para asignar prioridad.
        """
        vec = [1 if kw in (description or '').lower() else 0 for kw in self.features]
        idx = self.clf_prio.predict([vec])[0]
        return self.le_prio.inverse_transform([idx])[0]

    def crear_ticket(self):
        """
        Abre ventana para ingresar un ticket; aplica árboles de decisión para IA.
        """
        ventana = tk.Toplevel(self.root)
        ventana.title("Nuevo Ticket")

        tk.Label(ventana, text="Nombre del residente:").grid(row=0, column=0, padx=5, pady=5)
        nombre_entry = tk.Entry(ventana)
        nombre_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(ventana, text="Descripción:").grid(row=1, column=0, padx=5, pady=5)
        desc_text = tk.Text(ventana, width=40, height=5)
        desc_text.grid(row=1, column=1, padx=5, pady=5)

        def guardar():
            nombre = nombre_entry.get().strip()
            descripcion = desc_text.get('1.0', 'end').strip()
            if not nombre or not descripcion:
                messagebox.showwarning("Campos vacíos", "Nombre y descripción son obligatorios.")
                return
            categoria = self.classify_ticket(descripcion)
            prioridad = self.prioritize_ticket(categoria, descripcion)
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
            messagebox.showinfo("Éxito", f"Ticket generado. Categoría: {categoria}, Prioridad: {prioridad}.")
            ventana.destroy()

        tk.Button(ventana, text="Guardar", command=guardar).grid(row=2, column=0, columnspan=2, pady=10)

    def ver_historial(self):
        """
        Muestra todos los tickets con categoría y prioridad.
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
            messagebox.showwarning("Sin datos", "No hay tickets para reporte.")
            return
        stats_cat = {}
        stats_prio = {}
        for t in self.tickets:
            stats_cat[t['categoria']] = stats_cat.get(t['categoria'], 0) + 1
            stats_prio[t['prioridad']] = stats_prio.get(t['prioridad'], 0) + 1
        reporte = f"Total de tickets: {total}\n\nTickets por categoría:\n"
        for cat, cnt in stats_cat.items():
            reporte += f"- {cat}: {cnt}\n"
        reporte += "\nTickets por prioridad:\n"
        for pr, cnt in stats_prio.items():
            reporte += f"- {pr}: {cnt}\n"
        messagebox.showinfo("Reporte", reporte)

    def setup_ui(self):
        """
        Configura la ventana principal y menús.
        """
        self.root = tk.Tk()
        self.root.title("Agente de Gestión de Tickets Avanzado")
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
