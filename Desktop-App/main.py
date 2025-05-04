import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import random
import os
from PIL import Image
from CTkMessagebox import CTkMessagebox
import threading

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

def change_appearance_mode(new_appearance_mode):
    ctk.set_appearance_mode(new_appearance_mode)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.demand_dist = {
            "Good": {40: 0.03, 50: 0.05, 60: 0.15, 70: 0.20, 80: 0.35, 90: 0.15, 100: 0.07},
            "Fair": {40: 0.10, 50: 0.18, 60: 0.40, 70: 0.20, 80: 0.08, 90: 0.04, 100: 0.00},
            "Poor": {40: 0.44, 50: 0.22, 60: 0.16, 70: 0.12, 80: 0.06, 90: 0.00, 100: 0.00}
        }
        self.title("Newspaper Seller Simulation Dashboard")
        self.geometry(f"{1200}x{800}")
        self.minsize(1000, 600)
        self.path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets")
        self.grid_columnconfigure(0, weight=0, minsize=250)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.sidebar_frame = ctk.CTkScrollableFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.status_bar = ctk.CTkFrame(self, height=25, corner_radius=0)
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        self.settings_frame = ctk.CTkFrame(self, height=50, corner_radius=0)
        self.settings_frame.grid(row=1, column=0, columnspan=1, sticky="ew", padx=0, pady=(0, 0))
        self.settings_frame.grid_columnconfigure((0, 1), weight=1)
        self.simulation_status = tk.StringVar(value="Ready")
        status_label = ctk.CTkLabel(self.status_bar, textvariable=self.simulation_status, anchor="w")
        status_label.pack(side="left", padx=10, fill="x", expand=True)
        self.progress_bar = ctk.CTkProgressBar(self.status_bar, mode='indeterminate')
        self.progress_bar.set(0)
        self.progress_bar.pack(side="right", padx=10)
        self.initialize_variables()
        self.create_sidebar()
        self.create_main_content()
        self.setting_image = ctk.CTkImage(Image.open(os.path.join(self.path, "setting-icon.png")), size=(26, 26))
        self.theme_icon_label = ctk.CTkLabel(self.settings_frame, image=self.setting_image, text="", width=26, height=26, fg_color="transparent")
        self.theme_icon_label.bind("<Button-1>", lambda e: self.open_settings_window())
        self.theme_icon_label.grid(row=0, column=0, padx=(0, 20), pady=10, sticky="e")
        self.run_button = ctk.CTkButton(self.settings_frame, text=">> Run Simulation", command=self.run_simulation,
                                        fg_color="#28a745", hover_color="#218838", font=ctk.CTkFont(weight="bold"))
        self.run_button.grid(row=0, column=1, padx=(20, 0), pady=10, sticky="w")

    def open_settings_window(self):
        settings_window = ctk.CTkToplevel(self)
        settings_window.title("Settings")
        settings_window.geometry("300x200")
        settings_window.resizable(False, False)
        settings_window.transient(self)
        settings_window.grab_set()
        theme_label = ctk.CTkLabel(settings_window, text="Select Theme:")
        theme_label.pack(pady=(20, 10))
        theme_option_menu = ctk.CTkOptionMenu(settings_window, values=["Light", "Dark", "System"], command=lambda value: [change_appearance_mode(value), settings_window.destroy()])
        theme_option_menu.set(ctk.get_appearance_mode())
        theme_option_menu.pack(pady=10)
        close_button = ctk.CTkButton(settings_window, text="Close", command=settings_window.destroy)
        close_button.pack(pady=20)

    def initialize_variables(self):
        self.paper_sell_price = ctk.DoubleVar(value=0.5)
        self.paper_cost = ctk.DoubleVar(value=0.33)
        self.scrap_sale_price = ctk.DoubleVar(value=0.05)
        self.days = ctk.IntVar(value=30)
        self.quantity = ctk.IntVar(value=70)
        self.iterations = ctk.IntVar(value=100)
        self.good_prob = ctk.DoubleVar(value=0.35)
        self.fair_prob = ctk.DoubleVar(value=0.45)
        self.poor_prob = ctk.DoubleVar(value=0.20)
        self.simulation_results = None
        self.simulation_status = tk.StringVar(value="Ready")

        self.paper_sell_price.trace_add("write", lambda *args: self.validate_positive(self.paper_sell_price, "Paper Sell Price"))
        self.paper_cost.trace_add("write", lambda *args: self.validate_positive(self.paper_cost, "Paper Cost"))
        self.scrap_sale_price.trace_add("write", lambda *args: self.validate_positive(self.scrap_sale_price, "Scrap Sale Price"))
        self.days.trace_add("write", lambda *args: self.validate_positive(self.days, "Number of Days"))
        self.quantity.trace_add("write", lambda *args: self.validate_positive(self.quantity, "Paper Quantity"))
        self.iterations.trace_add("write", lambda *args: self.validate_positive(self.iterations, "Number of Iterations"))
        self.good_prob.trace_add("write", lambda *args: self.validate_prob(self.good_prob, "Good Day Probability"))
        self.fair_prob.trace_add("write", lambda *args: self.validate_prob(self.fair_prob, "Fair Day Probability"))
        self.poor_prob.trace_add("write", lambda *args: self.validate_prob(self.poor_prob, "Poor Day Probability"))

    def validate_positive(self, var, name):
        try:
            value = var.get()
            if value == "":
                return
            if float(value) < 0:
                CTkMessagebox(title="Invalid Value", message=f"{name} cannot be negative.", icon="warning")
                var.set(0)
        except ValueError:
            CTkMessagebox(title="Invalid Input", message=f"{name} must be a number.", icon="warning")
            var.set(0)

    def validate_prob(self, var, name):
        try:
            value = var.get()
            if value == "":
                return
            value = float(value)
            if value < 0 or value > 1:
                CTkMessagebox(title="Invalid Probability", message=f"{name} must be between 0 and 1.", icon="warning")
                var.set(0)
        except ValueError:
            CTkMessagebox(title="Invalid Input", message=f"{name} must be a number.", icon="warning")
            var.set(0)

    def reset(self):
        self.paper_sell_price.set(0.5)
        self.paper_cost.set(0.33)
        self.scrap_sale_price.set(0.05)
        self.days.set(30)
        self.quantity.set(70)
        self.iterations.set(100)
        self.good_prob.set(0.35)
        self.fair_prob.set(0.45)
        self.poor_prob.set(0.20)
        self.simulation_status.set("Parameters reset to defaults")

    def create_main_content(self):
        self.tabview = ctk.CTkTabview(self.content_frame)
        self.tabview.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.tab_results = self.tabview.add("Simulation")
        self.tab_viz = self.tabview.add("Visualizations")
        self.tab_results.grid_columnconfigure(0, weight=1)
        self.tab_results.grid_rowconfigure(0, weight=1)
        self.tab_viz.grid_columnconfigure(0, weight=1)
        self.tab_viz.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.setup_results_tab()
        self.setup_visualization_tab()

    def display_simulation_results(self):
        if not self.simulation_results: return
        params = self.simulation_results["Parameters"]
        summary = self.simulation_results["Summary"]
        self.summary_labels["Average Daily Profit"].configure(text=f"${summary['Average Daily Profit']:.2f}")
        self.summary_labels["Order Quantity"].configure(text=str(params["Quantity"]))
        self.summary_labels["Total Days Simulated"].configure(text=str(params["Days"]))
        self.summary_labels["Total Iterations"].configure(text=str(params["Iterations"]))
        self.summary_labels["Min Profit"].configure(text=f"${summary['Min Profit']:.2f}")
        self.summary_labels["Max Profit"].configure(text=f"${summary['Max Profit']:.2f}")

    def setup_results_tab(self):
        summary_frame = ctk.CTkFrame(self.tab_results)
        summary_frame.pack(fill="x", padx=10, pady=10)
        self.summary_labels = {}
        summary_titles = ["Average Daily Profit", "Order Quantity", "Total Days Simulated", "Total Iterations", "Min Profit", "Max Profit"]
        for i, title in enumerate(summary_titles):
            row, col = divmod(i, 3)
            label_frame = ctk.CTkFrame(summary_frame)
            label_frame.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            ctk.CTkLabel(label_frame, text=title, font=ctk.CTkFont(size=12)).pack(pady=(5, 0))
            value_label = ctk.CTkLabel(label_frame, text="--", font=ctk.CTkFont(size=14, weight="bold"))
            value_label.pack(pady=(0, 5))
            self.summary_labels[title] = value_label
        for i in range(3):
            summary_frame.grid_columnconfigure(i, weight=1)
        table_frame = ctk.CTkFrame(self.tab_results)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(table_frame, text="Simulation Results", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        tree_container = ttk.Frame(table_frame)
        tree_container.pack(fill="both", expand=True, padx=5, pady=5)
        columns = ("Day", "Day Type", "Demand", "Revenue", "Excess Demand", "Lost Profit", "Scraps", "Salvage", "Daily Profit")
        self.results_tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=15)
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=100, anchor="center")
        y_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.results_tree.yview)
        x_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal", command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        self.results_tree.grid(row=0, column=0, sticky="nsew")
        y_scrollbar.grid(row=0, column=1, sticky="ns")
        x_scrollbar.grid(row=1, column=0, sticky="ew")
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        control_frame = ctk.CTkFrame(self.tab_results)
        control_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(control_frame, text="Iteration:").pack(side="left", padx=(10, 5))
        self.iteration_var = tk.StringVar(value="1")
        self.iteration_combobox = ctk.CTkComboBox(control_frame, variable=self.iteration_var, values=["1"], command=self.update_results_display)
        self.iteration_combobox.pack(side="left", padx=5)
        export_button = ctk.CTkButton(control_frame, text="Export to CSV", command=self.export_results_to_csv)
        export_button.pack(side="right", padx=10)

    def export_results_to_csv(self):
        if not self.simulation_results:
            CTkMessagebox(title="No Data", message="No simulation data to export.", icon="warning")
            return
        iteration_idx = int(self.iteration_var.get()) - 1
        days_data = self.simulation_results["Iterations"][iteration_idx]["Days"]
        import csv
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, 'w', newline='') as csvfile:
                fieldnames = ["Day", "Day Type", "Demand", "Revenue", "Excess Demand", "Lost Profit", "Scraps", "Salvage", "Daily Profit"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for day_data in days_data:
                    writer.writerow({
                        "Day": day_data["Day"],
                        "Day Type": day_data["Day Type"],
                        "Demand": day_data["Demand"],
                        "Revenue": f"{day_data['Revenue']:.2f}",
                        "Excess Demand": day_data["Excess Demand"],
                        "Lost Profit": f"{day_data['Lost Profit']:.2f}",
                        "Scraps": day_data["Scraps"],
                        "Salvage": f"{day_data['Salvage']:.2f}",
                        "Daily Profit": f"{day_data['Daily Profit']:.2f}"
                    })
            CTkMessagebox(title="Export Successful", message=f"Data exported to {file_path}", icon="info")

    def setup_visualization_tab(self):
        self.viz_notebook = ttk.Notebook(self.tab_viz)
        self.viz_notebook.pack(fill="both", expand=True, padx=10, pady=10)
        daily_profit_frame = ttk.Frame(self.viz_notebook)
        self.viz_notebook.add(daily_profit_frame, text="Daily Profits")
        self.daily_profit_fig, self.daily_profit_ax = plt.subplots(figsize=(10, 6))
        self.daily_profit_canvas = FigureCanvasTkAgg(self.daily_profit_fig, daily_profit_frame)
        self.daily_profit_canvas.get_tk_widget().pack(fill="both", expand=True)
        NavigationToolbar2Tk(self.daily_profit_canvas, daily_profit_frame)
        # save_button1 = ctk.CTkButton(daily_profit_frame, text="Save Chart", command=lambda: self.save_figure(self.daily_profit_fig))
        # save_button1.pack(pady=5)
        demand_dist_frame = ttk.Frame(self.viz_notebook)
        self.viz_notebook.add(demand_dist_frame, text="Demand Distribution")
        self.demand_dist_fig, self.demand_dist_ax = plt.subplots(figsize=(10, 6))
        self.demand_dist_canvas = FigureCanvasTkAgg(self.demand_dist_fig, demand_dist_frame)
        self.demand_dist_canvas.get_tk_widget().pack(fill="both", expand=True)
        NavigationToolbar2Tk(self.demand_dist_canvas, demand_dist_frame)
        # save_button2 = ctk.CTkButton(demand_dist_frame, text="Save Chart", command=lambda: self.save_figure(self.demand_dist_fig))
        # save_button2.pack(pady=5)
        # New tab for Profit vs. Quantity
        # profit_quantity_frame = ttk.Frame(self.viz_notebook)
        # self.viz_notebook.add(profit_quantity_frame, text="Profit vs. Quantity")
        # self.profit_quantity_fig, self.profit_quantity_ax = plt.subplots(figsize=(10, 6))
        # self.profit_quantity_canvas = FigureCanvasTkAgg(self.profit_quantity_fig, profit_quantity_frame)
        # self.profit_quantity_canvas.get_tk_widget().pack(fill="both", expand=True)
        # NavigationToolbar2Tk(self.profit_quantity_canvas, profit_quantity_frame)
        # save_button3 = ctk.CTkButton(profit_quantity_frame, text="Save Chart", command=lambda: self.save_figure(self.profit_quantity_fig))
        # save_button3.pack(pady=5)

    def save_figure(self, fig):
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf")])
        if file_path:
            fig.savefig(file_path)
            CTkMessagebox(title="Save Successful", message=f"Chart saved to {file_path}", icon="info")

    def create_sidebar(self):
        cur = 0
        logo = ctk.CTkLabel(self.sidebar_frame, text="Newspaper Seller", font=ctk.CTkFont(size=20, weight="bold"))
        logo.grid(row=cur, column=0, padx=20, pady=(20, 10))
        cur += 1
        subtitle = ctk.CTkLabel(self.sidebar_frame, text="Simulation Dashboard", font=ctk.CTkFont(size=14))
        subtitle.grid(row=cur, column=0, padx=20, pady=(0, 20))
        cur += 1
        separator = ttk.Separator(self.sidebar_frame, orient='horizontal')
        separator.grid(row=cur, column=0, sticky="ew", padx=15, pady=10)
        cur += 1
        params = ctk.CTkLabel(self.sidebar_frame, text="Simulation Parameters", font=ctk.CTkFont(size=16, weight="bold"))
        params.grid(row=cur, column=0, padx=20, pady=(10, 10), sticky="w")
        cur += 1
        sell_label = ctk.CTkLabel(self.sidebar_frame, text="Paper Sell Price ($):")
        sell_label.grid(row=cur, column=0, padx=20, pady=(10, 0), sticky="w")
        cur += 1
        sell_entry = ctk.CTkEntry(self.sidebar_frame, width=80, textvariable=self.paper_sell_price)
        sell_entry.grid(row=cur, column=0, padx=20, pady=(5, 10), sticky="w")
        cur += 1
        cost_label = ctk.CTkLabel(self.sidebar_frame, text="Paper Cost ($):")
        cost_label.grid(row=cur, column=0, padx=20, pady=(10, 0), sticky="w")
        cur += 1
        cost_entry = ctk.CTkEntry(self.sidebar_frame, width=80, textvariable=self.paper_cost)
        cost_entry.grid(row=cur, column=0, padx=20, pady=(5, 10), sticky="w")
        cur += 1
        scrap_label = ctk.CTkLabel(self.sidebar_frame, text="Scrap Sale Price ($):")
        scrap_label.grid(row=cur, column=0, padx=20, pady=(10, 0), sticky="w")
        cur += 1
        scrap_entry = ctk.CTkEntry(self.sidebar_frame, width=80, textvariable=self.scrap_sale_price)
        scrap_entry.grid(row=cur, column=0, padx=20, pady=(5, 10), sticky="w")
        cur += 1
        days_label = ctk.CTkLabel(self.sidebar_frame, text="Number of Days:")
        days_label.grid(row=cur, column=0, padx=20, pady=(10, 0), sticky="w")
        cur += 1
        days_entry = ctk.CTkEntry(self.sidebar_frame, width=80, textvariable=self.days)
        days_entry.grid(row=cur, column=0, padx=20, pady=(5, 10), sticky="w")
        cur += 1
        quantity_label = ctk.CTkLabel(self.sidebar_frame, text=f"Paper Quantity: {self.quantity.get()}")
        quantity_label.grid(row=cur, column=0, padx=20, pady=(10, 0), sticky="w")
        cur += 1
        def update_quantity_label(value):
            quantity_label.configure(text=f"Paper Quantity: {int(float(value))}")
            self.quantity.set(int(float(value)))
        quantity_slider = ctk.CTkSlider(self.sidebar_frame, from_=40, to=100, number_of_steps=60, command=update_quantity_label)
        quantity_slider.set(self.quantity.get())
        quantity_slider.grid(row=cur, column=0, padx=20, pady=(5, 10), sticky="ew")
        cur += 1
        iterations_label = ctk.CTkLabel(self.sidebar_frame, text="Number of Iterations:")
        iterations_label.grid(row=cur, column=0, padx=20, pady=(10, 0), sticky="w")
        cur += 1
        self.iterations_value_label = ctk.CTkLabel(self.sidebar_frame, text=f"{self.iterations.get()} iterations")
        self.iterations_value_label.grid(row=cur, column=0, padx=20, pady=(5, 0), sticky="w")
        cur += 1
        def update_iterations_label(value):
            self.iterations_value_label.configure(text=f"{int(value)} iterations")
            self.iterations.set(int(value))
        iterations_slider = ctk.CTkSlider(self.sidebar_frame, from_=1, to=1000, number_of_steps=999, command=update_iterations_label)
        iterations_slider.set(self.iterations.get())
        iterations_slider.grid(row=cur, column=0, padx=20, pady=(5, 10), sticky="ew")
        cur += 1
        separator2 = ttk.Separator(self.sidebar_frame, orient='horizontal')
        separator2.grid(row=cur, column=0, sticky="ew", padx=15, pady=10)
        cur += 1
        probs_label = ctk.CTkLabel(self.sidebar_frame, text="Day Type Probabilities", font=ctk.CTkFont(size=16, weight="bold"))
        probs_label.grid(row=cur, column=0, padx=20, pady=(10, 10), sticky="w")
        cur += 1
        good_label = ctk.CTkLabel(self.sidebar_frame, text="Good Day Probability:")
        good_label.grid(row=cur, column=0, padx=20, pady=(10, 0), sticky="w")
        cur += 1
        good_entry = ctk.CTkEntry(self.sidebar_frame, width=80, textvariable=self.good_prob)
        good_entry.grid(row=cur, column=0, padx=20, pady=(5, 10), sticky="w")
        cur += 1
        fair_label = ctk.CTkLabel(self.sidebar_frame, text="Fair Day Probability:")
        fair_label.grid(row=cur, column=0, padx=20, pady=(10, 0), sticky="w")
        cur += 1
        fair_entry = ctk.CTkEntry(self.sidebar_frame, width=80, textvariable=self.fair_prob)
        fair_entry.grid(row=cur, column=0, padx=20, pady=(5, 10), sticky="w")
        cur += 1
        poor_label = ctk.CTkLabel(self.sidebar_frame, text="Poor Day Probability:")
        poor_label.grid(row=cur, column=0, padx=20, pady=(10, 0), sticky="w")
        cur += 1
        poor_entry = ctk.CTkEntry(self.sidebar_frame, width=80, textvariable=self.poor_prob)
        poor_entry.grid(row=cur, column=0, padx=20, pady=(5, 10), sticky="w")
        cur += 1
        def validate_probabilities(*args):
            total = self.good_prob.get() + self.fair_prob.get() + self.poor_prob.get()
            total_label.configure(text=f"Sum: {total:.2f}", text_color="green" if abs(total - 1.0) < 0.001 else "red")
        total_label = ctk.CTkLabel(self.sidebar_frame, text="Sum: 1.00", text_color="green")
        total_label.grid(row=cur, column=0, padx=20, pady=(5, 10), sticky="w")
        cur += 1
        self.good_prob.trace_add("write", validate_probabilities)
        self.fair_prob.trace_add("write", validate_probabilities)
        self.poor_prob.trace_add("write", validate_probabilities)
        separator3 = ttk.Separator(self.sidebar_frame, orient='horizontal')
        separator3.grid(row=cur, column=0, sticky="ew", padx=15, pady=10)
        cur += 1
        demand_button = ctk.CTkButton(self.sidebar_frame, text="Setup Demand Distribution", command=self.open_demand_distribution_window)
        demand_button.grid(row=cur, column=0, padx=20, pady=10, sticky="ew")
        cur += 1
        analyze_button = ctk.CTkButton(self.sidebar_frame, text="Analyze Profit vs. Quantity", command=self.open_analyze_dialog)
        analyze_button.grid(row=cur, column=0, padx=20, pady=10, sticky="ew")
        cur += 1
        reset_button = ctk.CTkButton(self.sidebar_frame, text="Reset Parameters", command=self.reset)
        reset_button.grid(row=cur, column=0, padx=20, pady=5, sticky="ew")
        cur += 1
        self.sidebar_frame.grid_rowconfigure(cur, weight=1)

    def open_analyze_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Analyze Profit vs. Quantity")
        dialog.geometry("300x200")
        min_label = ctk.CTkLabel(dialog, text="Min Quantity:")
        min_label.pack(pady=5)
        self.min_quantity_entry = ctk.CTkEntry(dialog)
        self.min_quantity_entry.pack(pady=5)
        max_label = ctk.CTkLabel(dialog, text="Max Quantity:")
        max_label.pack(pady=5)
        self.max_quantity_entry = ctk.CTkEntry(dialog)
        self.max_quantity_entry.pack(pady=5)
        step_label = ctk.CTkLabel(dialog, text="Step Size:")
        step_label.pack(pady=5)
        self.step_entry = ctk.CTkEntry(dialog)
        self.step_entry.pack(pady=5)
        run_button = ctk.CTkButton(dialog, text="Run Analysis", command=lambda: self.run_profit_quantity_analysis(dialog))
        run_button.pack(pady=10)

    def run_profit_quantity_analysis(self, dialog):
        try:
            min_qty = int(self.min_quantity_entry.get())
            max_qty = int(self.max_quantity_entry.get())
            step = int(self.step_entry.get())
            if min_qty >= max_qty or step <= 0:
                CTkMessagebox(title="Invalid Input", message="Please enter valid min, max, and step values.", icon="warning")
                return
            quantities = list(range(min_qty, max_qty + 1, step))
            dialog.destroy()
            self.simulation_status.set("Running profit vs. quantity analysis...")
            self.progress_bar.start()
            self.update_idletasks()
            def analysis_thread():
                results = []
                for qty in quantities:
                    self.after(0, lambda q=qty: self.simulation_status.set(f"Simulating quantity {q}..."))
                    avg_profit = self.simulate_for_quantity(qty)
                    results.append((qty, avg_profit))
                self.after(0, lambda: self.on_analysis_complete(results))
            threading.Thread(target=analysis_thread, daemon=True).start()
        except ValueError:
            CTkMessagebox(title="Invalid Input", message="Please enter integer values for quantities and step.", icon="warning")

    def simulate_for_quantity(self, quantity):
        p = self.paper_sell_price.get()
        c = self.paper_cost.get()
        s = self.scrap_sale_price.get()
        days = self.days.get()
        iterations = self.iterations.get()
        day_type_probs = {"Good": self.good_prob.get(), "Fair": self.fair_prob.get(), "Poor": self.poor_prob.get()}
        cum_day_type_prob = {}
        cumulative = 0.0
        for day_type, prob in sorted(day_type_probs.items()):
            cumulative += prob
            cum_day_type_prob[day_type] = cumulative
        if not hasattr(self, 'cum_demand_dist'):
            self.calculate_cumulative_distributions()
        total_profits = []
        for iteration in range(iterations):
            iteration_profit = 0
            for day in range(1, days + 1):
                day_rnd = random.random()
                day_type = "Poor"
                for dtype, cum_prob in cum_day_type_prob.items():
                    if day_rnd < cum_prob:
                        day_type = dtype
                        break
                demand_rnd = random.random()
                demand = 0
                for d, cum_prob in sorted(self.cum_demand_dist[day_type].items()):
                    if demand_rnd < cum_prob:
                        demand = d
                        break
                revenue = min(demand, quantity) * p
                excess_demand = max(0, demand - quantity)
                lost_profit = excess_demand * (p - c)
                num_scraps = max(0, quantity - demand)
                salvage = num_scraps * s
                daily_profit = revenue - (quantity * c) + salvage
                iteration_profit += daily_profit
            total_profits.append(iteration_profit / days)
        avg_profit = sum(total_profits) / iterations
        return avg_profit

    def on_analysis_complete(self, results):
        self.progress_bar.stop()
        self.simulation_status.set("Analysis complete.")
        quantities, profits = zip(*results)
        self.profit_quantity_ax.clear()
        self.profit_quantity_ax.plot(quantities, profits, marker='o')
        self.profit_quantity_ax.set(xlabel='Number of Newspapers', ylabel='Average Profit ($)', title='Average Profit vs. Quantity')
        self.profit_quantity_canvas.draw()

    def run_simulation(self):
        if not self.validate_parameters():
            return
        self.simulation_status.set("Running simulation...")
        self.progress_bar.start()
        self.run_button.configure(state="disabled")
        self.update_idletasks()
        def simulation_thread():
            p = self.paper_sell_price.get()
            c = self.paper_cost.get()
            s = self.scrap_sale_price.get()
            days = self.days.get()
            quantity = self.quantity.get()
            iterations = self.iterations.get()
            day_type_probs = {"Good": self.good_prob.get(), "Fair": self.fair_prob.get(), "Poor": self.poor_prob.get()}
            cum_day_type_prob = {}
            cumulative = 0.0
            for day_type, prob in sorted(day_type_probs.items()):
                cumulative += prob
                cum_day_type_prob[day_type] = cumulative
            if not hasattr(self, 'cum_demand_dist'):
                self.calculate_cumulative_distributions()
            all_results = []
            for iteration in range(iterations):
                iteration_results = []
                for day in range(1, days + 1):
                    day_rnd = random.random()
                    day_type = "Poor"
                    for dtype, cum_prob in cum_day_type_prob.items():
                        if day_rnd < cum_prob:
                            day_type = dtype
                            break
                    demand_rnd = random.random()
                    demand = 0
                    for d, cum_prob in sorted(self.cum_demand_dist[day_type].items()):
                        if demand_rnd < cum_prob:
                            demand = d
                            break
                    revenue = min(demand, quantity) * p
                    excess_demand = max(0, demand - quantity)
                    lost_profit = excess_demand * (p - c)
                    num_scraps = max(0, quantity - demand)
                    salvage = num_scraps * s
                    daily_profit = revenue - (quantity * c) + salvage
                    day_result = {
                        "Day": day, "Day Random": day_rnd, "Day Type": day_type, "Demand Random": demand_rnd,
                        "Demand": demand, "Revenue": revenue, "Excess Demand": excess_demand, "Lost Profit": lost_profit,
                        "Scraps": num_scraps, "Salvage": salvage, "Daily Profit": daily_profit
                    }
                    iteration_results.append(day_result)
                total_profit = sum(result["Daily Profit"] for result in iteration_results)
                avg_profit = total_profit / days
                iteration_summary = {"Iteration": iteration + 1, "Total Profit": total_profit, "Average Profit": avg_profit, "Days": iteration_results}
                all_results.append(iteration_summary)
            total_profits = [result["Total Profit"] for result in all_results]
            avg_total_profit = sum(total_profits) / iterations
            avg_daily_profit = avg_total_profit / days
            overall_summary = {
                "Average Total Profit": avg_total_profit, "Average Daily Profit": avg_daily_profit, "Quantity": quantity,
                "Min Profit": min(total_profits), "Max Profit": max(total_profits)
            }
            simulation_results = {
                "Parameters": {
                    "Paper Sell Price": p, "Paper Cost": c, "Scrap Sale Price": s, "Days": days, "Quantity": quantity,
                    "Iterations": iterations, "Day Type Probabilities": day_type_probs
                },
                "Iterations": all_results, "Summary": overall_summary
            }
            self.after(0, lambda: self.on_simulation_complete(simulation_results))
        threading.Thread(target=simulation_thread, daemon=True).start()

    def on_simulation_complete(self, simulation_results):
        self.simulation_results = simulation_results
        self.progress_bar.stop()
        avg_daily_profit = simulation_results["Summary"]["Average Daily Profit"]
        self.simulation_status.set(f"Simulation complete. Avg. Daily Profit: ${avg_daily_profit:.2f}")
        self.run_button.configure(state="normal")
        self.display_simulation_results()
        iterations = simulation_results["Parameters"]["Iterations"]
        iteration_values = [str(i) for i in range(1, iterations + 1)]
        self.iteration_combobox.configure(values=iteration_values)
        self.iteration_var.set("1")
        self.update_results_display("1")
        self.tabview.set("Simulation")

    def update_results_display(self, iteration_str):
        iteration_idx = int(iteration_str) - 1
        if not self.simulation_results or iteration_idx >= len(self.simulation_results["Iterations"]):
            return
        days_data = self.simulation_results["Iterations"][iteration_idx]["Days"]
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        for day_data in days_data:
            self.results_tree.insert("", "end", values=(
                day_data["Day"], day_data["Day Type"], day_data["Demand"], f"${day_data['Revenue']:.2f}",
                day_data["Excess Demand"], f"${day_data['Lost Profit']:.2f}", day_data["Scraps"], f"${day_data['Salvage']:.2f}",
                f"${day_data['Daily Profit']:.2f}"
            ))
        self.update_visualizations()

    def update_visualizations(self):
        if not self.simulation_results:
            return
        iteration_idx = int(self.iteration_var.get()) - 1
        days_data = self.simulation_results["Iterations"][iteration_idx]["Days"]
        self.daily_profit_ax.clear()
        days = [d["Day"] for d in days_data]
        profits = [d["Daily Profit"] for d in days_data]
        self.daily_profit_ax.bar(days, profits, color='skyblue', label='Daily Profit')
        avg_profit = np.mean(profits)
        self.daily_profit_ax.axhline(y=avg_profit, color='r', linestyle='-', label=f'Avg: ${avg_profit:.2f}')
        self.daily_profit_ax.set(xlabel='Day', ylabel='Profit ($)', title=f'Daily Profits (Iteration {iteration_idx + 1})')
        self.daily_profit_ax.legend()
        self.daily_profit_canvas.draw()
        self.demand_dist_ax.clear()
        demands = sorted(self.demand_dist["Good"].keys())
        width = 0.25
        for i, day_type in enumerate(["Good", "Fair", "Poor"]):
            probs = [self.demand_dist[day_type][d] for d in demands]
            self.demand_dist_ax.bar(np.arange(len(demands)) + i * width, probs, width, label=day_type)
        self.demand_dist_ax.set_xticks(np.arange(len(demands)) + width, demands)
        self.demand_dist_ax.set(xlabel='Demand', ylabel='Probability', title='Demand Distribution by Day Type')
        self.demand_dist_ax.legend()
        self.demand_dist_canvas.draw()

    def validate_parameters(self):
        total_prob = self.good_prob.get() + self.fair_prob.get() + self.poor_prob.get()
        if abs(total_prob - 1.0) > 0.001:
            CTkMessagebox(title="Invalid Probabilities", message="Day type probabilities must sum to 1.", icon="warning")
            return False
        return True

    def open_demand_distribution_window(self):
        demand_window = ctk.CTkToplevel(self)
        demand_window.title("Demand Distribution Setup")
        demand_window.geometry("500x600")
        demand_window.transient(self)
        demand_window.grab_set()
        notebook = ttk.Notebook(demand_window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        tab_frames = {}
        entry_vars = {}
        for day_type in ["Good", "Fair", "Poor"]:
            tab = ttk.Frame(notebook)
            notebook.add(tab, text=day_type)
            tab_frames[day_type] = tab
            ttk.Label(tab, text=f"Demand Distribution for {day_type} Days", font=('TkDefaultFont', 12, 'bold')).grid(row=0, column=0, columnspan=3, pady=10)
            ttk.Label(tab, text="Demand").grid(row=1, column=0, padx=10, pady=5)
            ttk.Label(tab, text="Probability").grid(row=1, column=1, padx=10, pady=5)
            entry_vars[day_type] = {}
            for i, demand in enumerate([40, 50, 60, 70, 80, 90, 100]):
                ttk.Label(tab, text=str(demand)).grid(row=i + 2, column=0, padx=10, pady=5)
                prob_var = tk.DoubleVar(value=self.demand_dist[day_type].get(demand, 0.0))
                entry_vars[day_type][demand] = prob_var
                prob_entry = ttk.Entry(tab, textvariable=prob_var, width=10)
                prob_entry.grid(row=i + 2, column=1, padx=10, pady=5)
                prob_var.trace_add("write", lambda *args, v=prob_var, n=f"{day_type} Demand {demand}": self.validate_prob(v, n))
            sum_label = ttk.Label(tab, text="Sum: 0.00")
            sum_label.grid(row=9, column=0, columnspan=2, pady=10)
            def update_sum(day_type=day_type, label=sum_label):
                total = sum(var.get() for var in entry_vars[day_type].values())
                label.config(text=f"Sum: {total:.2f}", foreground="green" if abs(total - 1.0) < 0.001 else "red")
            for var in entry_vars[day_type].values():
                var.trace_add("write", lambda *args, dt=day_type, lbl=sum_label: update_sum(dt, lbl))
            update_sum(day_type, sum_label)
        def save_distributions():
            for day_type in ["Good", "Fair", "Poor"]:
                for demand, var in entry_vars[day_type].items():
                    self.demand_dist[day_type][demand] = var.get()
            self.calculate_cumulative_distributions()
            demand_window.destroy()
            self.simulation_status.set("Demand distributions updated")
        button_frame = ttk.Frame(demand_window)
        button_frame.pack(fill='x', padx=5, pady=5)
        ttk.Button(button_frame, text="Save", command=save_distributions).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Cancel", command=demand_window.destroy).pack(side='right', padx=5)

    def calculate_cumulative_distributions(self):
        self.cum_demand_dist = {}
        for day_type in self.demand_dist:
            self.cum_demand_dist[day_type] = {}
            cumulative = 0.0
            for demand in sorted(self.demand_dist[day_type].keys()):
                prob = self.demand_dist[day_type][demand]
                cumulative += prob
                self.cum_demand_dist[day_type][demand] = cumulative

if __name__ == "__main__":
    app = App()
    app.mainloop()
