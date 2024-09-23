import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
from tkinter import filedialog
import os

current_figure = None  # Pour garder une trace de la figure actuelle

# Fonction pour tracer le graphique sélectionné avec personnalisation
def plot_graph():
    global current_figure
    try:
        # Récupérer les données entrées
        data = [float(i) for i in entry_data.get().split(',')]
        unit_x = unit_var.get()  # Récupérer l'unité choisie pour l'axe X
        graph_type = graph_type_var.get()  # Récupérer le type de graphique choisi
        color = color_var.get()  # Récupérer la couleur choisie
        title = entry_title.get()  # Titre du graphique
        xlabel = entry_xlabel.get()  # Titre de l'axe X
        ylabel = entry_ylabel.get()  # Titre de l'axe Y

        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)

        # Générer des x en fonction de la longueur des données
        x = np.arange(len(data))

        # Tracer en fonction du type de graphique choisi
        if graph_type == "Courbe":
            ax.plot(x, data, color=color)
        elif graph_type == "Barres":
            ax.bar(x, data, color=color)
        elif graph_type == "Barres horizontales":
            ax.barh(x, data, color=color)
        elif graph_type == "Secteurs":
            colors = plt.cm.Paired(np.linspace(0, 1, len(data)))
            ax.pie(data, labels=[f'Donnée {i+1}' for i in range(len(data))], autopct='%1.1f%%', colors=colors)
            ax.axis('equal')  # Assurer que le graphique de secteurs soit circulaire
        elif graph_type == "Histogramme":
            ax.hist(data, bins=10, color=color)
        elif graph_type == "Nuage de points":
            ax.scatter(x, data, color=color)
        elif graph_type == "Box Plot":
            ax.boxplot(data)
            ax.set_title(title)
        elif graph_type == "Heatmap":
            heatmap_data = np.array(data).reshape(2, 2)  # Exemple pour créer une heatmap
            cax = ax.matshow(heatmap_data, cmap='viridis')

        # Personnalisation des axes et du titre si ce n'est pas un graphique de secteurs
        if graph_type not in ["Secteurs", "Box Plot", "Heatmap"]:
            ax.set_xlabel(f'{xlabel} ({unit_x})')
            ax.set_ylabel(ylabel)
            ax.set_title(title)

        # Afficher le graphique dans le cadre
        for widget in frame_graph.winfo_children():
            widget.destroy()  # Nettoyer l'ancien graphique avant d'afficher le nouveau

        canvas = FigureCanvasTkAgg(fig, master=frame_graph)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill='both')
        current_figure = fig  # Mettre à jour la figure actuelle

    except ValueError:
        label_error.configure(text="Erreur: Veuillez entrer des données numériques valides.")

# Fonction pour exporter le graphique ou les données
def export_data():
    export_type = export_var.get()
    if export_type == "PNG" and current_figure:
        file_path = filedialog.asksaveasfilename(defaultextension=".png", 
                                                 filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if file_path:
            current_figure.savefig(file_path)
            label_error.configure(text=f"Graphique sauvegardé sous {os.path.basename(file_path)}")
    else:
        data = entry_data.get().split(',')
        df = pd.DataFrame(data, columns=["Données"])

        if export_type == "CSV":
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", 
                                                     filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
            if file_path:
                df.to_csv(file_path, index=False)
                label_error.configure(text=f"Données sauvegardées sous {os.path.basename(file_path)}")
        elif export_type == "Excel":
            file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", 
                                                     filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
            if file_path:
                df.to_excel(file_path, index=False)
                label_error.configure(text=f"Données sauvegardées sous {os.path.basename(file_path)}")

# Fonction pour importer des données
def import_data():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")])
    if file_path:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
            entry_data.delete(0, ctk.END)
            entry_data.insert(0, ', '.join(df['Données'].astype(str).tolist()))
        elif file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
            entry_data.delete(0, ctk.END)
            entry_data.insert(0, ', '.join(df['Données'].astype(str).tolist()))
        label_error.configure(text=f"Données importées depuis {os.path.basename(file_path)}")

# Création de la fenêtre principale
app = ctk.CTk()
app.geometry("800x600")
app.title("Générateur de Graphiques")

# Utilisation d'une grille pour l'UI façon dashboard
app.grid_rowconfigure(0, weight=1)
app.grid_columnconfigure(0, weight=1)
app.grid_columnconfigure(1, weight=3)

# Section de gauche : options et entrées (cadre défilant)
frame_options = ctk.CTkScrollableFrame(app)
frame_options.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

# Instructions sur les types de données
label_data_instructions = ctk.CTkLabel(frame_options, text="Instructions :\n"
    "- Pour les barres horizontales : entrez les valeurs sous la forme\n"
    "  'valeur1, valeur2, valeur3'.\n"
    "- Pour la heatmap : entrez les valeurs sous la forme\n"
    "  'valeur1, valeur2, valeur3, valeur4' pour une matrice 2x2.\n"
    "  Exemple : '1, 2, 3, 4'.")
label_data_instructions.pack(padx=10, pady=5, fill='x')

# Label et entrée pour les données
label_data = ctk.CTkLabel(frame_options, text="Données (séparées par virgules) :")
label_data.pack(padx=10, pady=5, anchor="w")
entry_data = ctk.CTkEntry(frame_options)
entry_data.pack(padx=10, pady=5, fill='x')

# Menu déroulant pour sélectionner une unité
label_unit = ctk.CTkLabel(frame_options, text="Unité pour l'axe des X :")
label_unit.pack(padx=10, pady=5, anchor="w")
unit_var = ctk.StringVar(value="Secondes")
units = ["Secondes", "Minutes", "Heures", "Jours"]
unit_menu = ctk.CTkOptionMenu(frame_options, variable=unit_var, values=units)
unit_menu.pack(padx=10, pady=5, fill='x')

# Menu déroulant pour sélectionner le type de graphique
label_graph_type = ctk.CTkLabel(frame_options, text="Type de graphique :")
label_graph_type.pack(padx=10, pady=5, anchor="w")
graph_type_var = ctk.StringVar(value="Courbe")
graph_types = [
    "Courbe", "Barres", "Barres horizontales", 
    "Secteurs", "Histogramme", "Nuage de points", "Box Plot", "Heatmap"
]
graph_type_menu = ctk.CTkOptionMenu(frame_options, variable=graph_type_var, values=graph_types)
graph_type_menu.pack(padx=10, pady=5, fill='x')

# Menu déroulant pour sélectionner la couleur
label_color = ctk.CTkLabel(frame_options, text="Couleur du graphique :")
label_color.pack(padx=10, pady=5, anchor="w")
color_var = ctk.StringVar(value="blue")
colors = ["blue", "red", "green", "purple", "orange"]
color_menu = ctk.CTkOptionMenu(frame_options, variable=color_var, values=colors)
color_menu.pack(padx=10, pady=5, fill='x')

# Entrées pour le titre du graphique et des axes
label_title = ctk.CTkLabel(frame_options, text="Titre du graphique :")
label_title.pack(padx=10, pady=5, anchor="w")
entry_title = ctk.CTkEntry(frame_options, width=200)
entry_title.pack(padx=10, pady=5, fill='x')

label_xlabel = ctk.CTkLabel(frame_options, text="Titre de l'axe X :")
label_xlabel.pack(padx=10, pady=5, anchor="w")
entry_xlabel = ctk.CTkEntry(frame_options, width=200)
entry_xlabel.pack(padx=10, pady=5, fill='x')

label_ylabel = ctk.CTkLabel(frame_options, text="Titre de l'axe Y :")
label_ylabel.pack(padx=10, pady=5, anchor="w")
entry_ylabel = ctk.CTkEntry(frame_options, width=200)
entry_ylabel.pack(padx=10, pady=5, fill='x')

# Bouton pour générer un graphique
btn_plot = ctk.CTkButton(frame_options, text="Tracer le graphique", command=plot_graph)
btn_plot.pack(padx=10, pady=20)

# Menu déroulant pour sélectionner le type d'exportation
label_export_type = ctk.CTkLabel(frame_options, text="Type d'exportation :")
label_export_type.pack(padx=10, pady=5, anchor="w")
export_var = ctk.StringVar(value="PNG")
export_types = ["PNG", "CSV", "Excel"]
export_type_menu = ctk.CTkOptionMenu(frame_options, variable=export_var, values=export_types)
export_type_menu.pack(padx=10, pady=5, fill='x')



# Bouton pour exporter les données ou le graphique
btn_export = ctk.CTkButton(frame_options, text="Exporter", command=export_data)
btn_export.pack(padx=10, pady=10)


# Bouton pour importer des données
btn_import = ctk.CTkButton(frame_options, text="Importer CSV/Excel", command=import_data)
btn_import.pack(padx=10, pady=10)


# Label pour les messages d'erreur ou succès
label_error = ctk.CTkLabel(frame_options, text="", text_color="red")
label_error.pack(padx=10, pady=5, anchor="w")

# Section de droite : affichage du graphique
frame_graph = ctk.CTkFrame(app)
frame_graph.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

app.mainloop()
