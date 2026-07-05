import os
import json
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# aparência padrão do sistema
ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")  

TOTAL_REQUIRED = 230
AZUL_PADRAO = "#457B9D"
AZUL_HOVER = "#1D3557"

# mapeamento com as regras e cores de destaque
RULES = {
    "Pesquisa": {
        "min": 10, "max": 150, "color": "#8A2BE2",
        "subs": {
            "Iniciação científica": {"min": 0, "max": 120},
            "Publicações": {"min": 0, "max": 120},
            "Participação em projetos de pesquisa": {"min": 0, "max": 100},
            "Assistência a monografias, teses e dissertações": {"min": 0, "max": 40}
        }
    },
    "Extensão": {
        "min": 20, "max": 150, "color": "#E63946",
        "subs": {
            "Organização e/ou colaboração em eventos e atividades institucionais": {"min": 0, "max": 80},
            "Seminários, conferências, palestras, oficinas e visitas técnicas": {"min": 10, "max": 60},
            "Participação em projetos de extensão": {"min": 0, "max": 100},
            "Presença em bancas de projeto final de curso": {"min": 6, "max": 20},
            "Cursos de atualização, qualificação e certificação tecnológica": {"min": 0, "max": 100},
            "Cursos de língua estrangeira": {"min": 0, "max": 60},
            "Assistência, assessoria e consultoria técnica": {"min": 0, "max": 100}
        }
    },
    "Ensino": {
        "min": 0, "max": 150, "color": "#2A9D8F",
        "subs": {
            "Disciplinas não previstas": {"min": 0, "max": 120},
            "Monitoria": {"min": 0, "max": 100}
        }
    },
    "Conscientização": {
        "min": 0, "max": 20, "color": "#E9C46A",
        "subs": {
            "Atividade Única de Conscientização": {"min": 0, "max": 20}
        }
    }
}

# sub-cores para o detalhamento interno
SUB_COLORS = ["#457B9D", "#1D3557", "#A8DADC", "#4EA8DE", "#56CFE1", "#72EFDD", "#80FFDB"]
DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

class CableApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Cable - Gestor de Horas Complementares CEFET/RJ")
        self.geometry("1200x780")
        
        self.activities = load_data()
        self.selected_type = "Pesquisa"
        self.viewing_sub_chart = False  
        
        self.setup_ui()
        
    def calculate_hours(self):
        raw_subs = {g: {s: 0 for s in RULES[g]["subs"]} for g in RULES}
        valid_subs = {g: {s: 0 for s in RULES[g]["subs"]} for g in RULES}
        valid_generals = {g: 0 for g in RULES}
        
        for act in self.activities:
            g, s, h = act["type"], act["category"], act["hours"]
            if g in raw_subs and s in raw_subs[g]:
                raw_subs[g][s] += h

        for g in RULES:
            sum_valid_subs = 0
            for s in RULES[g]["subs"]:
                valid_subs[g][s] = min(raw_subs[g][s], RULES[g]["subs"][s]["max"])
                sum_valid_subs += valid_subs[g][s]
            valid_generals[g] = min(sum_valid_subs, RULES[g]["max"])
            
        total_computed = sum(valid_generals.values())
        return raw_subs, valid_subs, valid_generals, total_computed

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # SIDEBAR
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        logo = ctk.CTkLabel(self.sidebar, text="Cable", font=ctk.CTkFont(size=26, weight="bold"), text_color=AZUL_PADRAO)
        logo.pack(pady=(30, 20), padx=20)
        
        btn_add = ctk.CTkButton(self.sidebar, text="+ Nova Atividade", command=self.open_add_window, fg_color=AZUL_PADRAO, hover_color=AZUL_HOVER)
        btn_add.pack(pady=10, padx=20, fill="x")
        
        self.btn_global_chart = ctk.CTkButton(self.sidebar, text="📊 Ver Gráfico Geral", fg_color=AZUL_PADRAO, hover_color=AZUL_HOVER, command=self.show_general_chart_view)
        self.btn_global_chart.pack(pady=(20, 10), padx=20, fill="x")
        
        lbl_filter = ctk.CTkLabel(self.sidebar, text="Categorias", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray")
        lbl_filter.pack(pady=(20, 5), padx=20, anchor="w")
        
        for category in RULES.keys():
            btn = ctk.CTkButton(self.sidebar, text=category, fg_color="transparent", text_color="white", anchor="w", command=lambda c=category: self.select_category(c))
            btn.pack(pady=2, padx=20, fill="x")
            
        # MAIN CONTENT
        self.main_content = ctk.CTkScrollableFrame(self)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(1, weight=1)
        
        self.render_dashboard()
        
    def select_category(self, category):
        self.selected_type = category
        self.viewing_sub_chart = True 
        self.render_dashboard()

    def show_general_chart_view(self):
        self.viewing_sub_chart = False
        self.render_dashboard()

    def toggle_chart_view(self, event=None):
        self.viewing_sub_chart = not self.viewing_sub_chart
        self.render_dashboard()

    def render_dashboard(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()
            
        raw_subs, valid_subs, valid_generals, total_computed = self.calculate_hours()
        hours_left = max(0, TOTAL_REQUIRED - total_computed)
        
        # HEADER
        header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        
        title_text = f"Progresso Acadêmico: {total_computed:.1f} / {TOTAL_REQUIRED}h"
        lbl_title = ctk.CTkLabel(header_frame, text=title_text, font=ctk.CTkFont(size=22, weight="bold"))
        lbl_title.pack(side="left", anchor="w")
        
        if total_computed >= TOTAL_REQUIRED:
            lbl_status = ctk.CTkLabel(header_frame, text="🎉 REQUISITO TOTAL ATINGIDO!", text_color="#2A9D8F", font=ctk.CTkFont(size=14, weight="bold"))
            lbl_status.pack(side="right", padx=10)
        else:
            lbl_status = ctk.CTkLabel(header_frame, text=f"Faltam {hours_left:.1f}h para a meta.", text_color=AZUL_PADRAO, font=ctk.CTkFont(size=14, weight="bold"))
            lbl_status.pack(side="right", padx=10)

        # CARDS DE RESUMO
        cards_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        cards_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        cards_frame.grid_columnconfigure((0,1,2,3), weight=1)
        
        for idx, cat in enumerate(RULES.keys()):
            is_selected = (cat == self.selected_type and self.viewing_sub_chart)
            card = ctk.CTkFrame(cards_frame, corner_radius=15, border_width=2 if is_selected else 0, border_color=RULES[cat]["color"])
            card.grid(row=0, column=idx, padx=5, pady=5, sticky="nsew")
            
            card.bind("<Button-1>", lambda e, c=cat: self.select_category(c))
            
            lbl_cat = ctk.CTkLabel(card, text=cat, font=ctk.CTkFont(size=13, weight="bold"), text_color=RULES[cat]["color"])
            lbl_cat.pack(pady=(10, 2))
            
            v_hrs = valid_generals[cat]
            lbl_hrs = ctk.CTkLabel(card, text=f"{v_hrs:.1f}h válidas\n(Teto: {RULES[cat]['max']}h)", font=ctk.CTkFont(size=11), text_color="white")
            lbl_hrs.pack(pady=2)
            
            if v_hrs < RULES[cat]["min"]:
                lbl_min = ctk.CTkLabel(card, text=f"Faltam {RULES[cat]['min'] - v_hrs:.1f}h", text_color="#E63946", font=ctk.CTkFont(size=10, weight="bold"))
            else:
                lbl_min = ctk.CTkLabel(card, text="Mínimo cumprido ✓", text_color="#2A9D8F", font=ctk.CTkFont(size=10))
            lbl_min.pack(pady=(2, 10))

        # CONTAINER DO GRÁFICO E DETALHAMENTO
        if self.viewing_sub_chart:
            chart_frame = ctk.CTkFrame(self.main_content, height=360)
            chart_frame.grid(row=2, column=0, padx=(0, 10), sticky="nsew")
            
            lbl_chart_info = ctk.CTkLabel(chart_frame, text="Gráfico: Subcategorias", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray")
            lbl_chart_info.pack(pady=5)
            
            self.render_sub_chart(chart_frame, valid_subs[self.selected_type])
            
            # seção de detalhamento à direita
            list_frame = ctk.CTkFrame(self.main_content, height=360)
            list_frame.grid(row=2, column=1, padx=(10, 0), sticky="nsew")
            
            lbl_list_title = ctk.CTkLabel(list_frame, text=f"Detalhamento: {self.selected_type}", font=ctk.CTkFont(size=15, weight="bold"), text_color=RULES[self.selected_type]["color"])
            lbl_list_title.pack(pady=10, padx=10, anchor="w")
            
            scroll_list = ctk.CTkScrollableFrame(list_frame, height=260)
            scroll_list.pack(fill="both", expand=True, padx=10, pady=10)
            
            filtered = [a for a in self.activities if a["type"] == self.selected_type]
            
            if not filtered:
                ctk.CTkLabel(scroll_list, text="Nenhum registro nesta categoria.", text_color="gray").pack(pady=30)
            else:
                for act in filtered:
                    item_frame = ctk.CTkFrame(scroll_list)
                    item_frame.pack(fill="x", pady=3, padx=2)
                    
                    txt = f"[{act['hours']:.1f}h] {act['name']}\nSub: {act['category']}\nData: {act['start_date']} | Obs: {act['observations']}"
                    lbl_item = ctk.CTkLabel(item_frame, text=txt, justify="left", font=ctk.CTkFont(size=11), anchor="w")
                    lbl_item.pack(side="left", padx=10, pady=5, fill="x", expand=True)
                    
                    btn_del = ctk.CTkButton(item_frame, text="X", width=25, fg_color="#E63946", hover_color="#8B0000", command=lambda a=act: self.delete_activity(a))
                    btn_del.pack(side="right", padx=5)
                    
                    btn_edit = ctk.CTkButton(item_frame, text="✏️", width=25, fg_color="gray", hover_color="#555555", command=lambda a=act: self.open_add_window(a))
                    btn_edit.pack(side="right", padx=5)

            # seção inferior para alertas de subcategorias mínimas não cumpridas
            sub_status_text = ""
            for s, r in RULES[self.selected_type]["subs"].items():
                if r["min"] > 0:
                    cumprido = valid_subs[self.selected_type][s]
                    if cumprido < r["min"]:
                        sub_status_text += f"⚠️ Requer Mínimo Obrigatório: {s} (Faltam {r['min']-cumprido:.1f}h)\n"
            
            if sub_status_text:
                alerts_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
                alerts_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(20, 0), padx=5)
                
                lbl_sub_alerts = ctk.CTkLabel(alerts_frame, text=sub_status_text.strip(), justify="left", text_color="#E63946", font=ctk.CTkFont(size=12, weight="bold"))
                lbl_sub_alerts.pack(anchor="w", padx=10, pady=10)

        else:
            #layout gráfico geral
            chart_frame = ctk.CTkFrame(self.main_content, height=380)
            chart_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5)
            
            lbl_chart_info = ctk.CTkLabel(chart_frame, text="Gráfico: Visão Geral", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray")
            lbl_chart_info.pack(pady=5)
            
            self.render_general_chart(chart_frame, valid_generals, hours_left)

    def render_general_chart(self, frame, valid_generals, hours_left):
        labels = list(valid_generals.keys())
        values = list(valid_generals.values())
        colors = [RULES[g]["color"] for g in labels]
        
        if hours_left > 0:
            labels.append("Faltam")
            values.append(hours_left)
            colors.append('#333333')
            
        self.plot_pie(frame, values, labels, colors, figsize=(7.2, 3.4))

    def render_sub_chart(self, frame, sub_dict):
        labels = [k for k, v in sub_dict.items() if v > 0]
        values = [v for k, v in sub_dict.items() if v > 0]
        
        if sum(values) == 0:
            self.plot_pie(frame, [1], ["Sem registros na categoria"], ["#333333"], figsize=(5.5, 3.4))
            return

        short_labels = [l[:15] + "..." if len(l) > 15 else l for l in labels]
        colors = SUB_COLORS[:len(values)]
        self.plot_pie(frame, values, short_labels, colors, figsize=(5.5, 3.4))

    def plot_pie(self, frame, values, labels, colors, figsize):
        fig, ax = plt.subplots(figsize=figsize, dpi=100)
        fig.patch.set_facecolor('none')
        ax.set_facecolor('none')
        
        wedges, _ = ax.pie(
            values, startangle=140, colors=colors, 
            wedgeprops=dict(width=0.35, edgecolor='none')
        )
        
        total = sum(values)
        legend_labels = []
        for l, v in zip(labels, values):
            if "Sem registros" in l or total == 0:
                legend_labels.append(l)
            else:
                pct = (v / total) * 100
                legend_labels.append(f"{l} ({v:.1f}h - {pct:.1f}%)")

        ax.legend(
            wedges, legend_labels, title="Legenda", loc="center left", 
            bbox_to_anchor=(1.0, 0.5), fontsize=8, 
            labelcolor="white", facecolor="#1E1E1E", edgecolor="none"
        )
        
        plt.tight_layout()
        chart = FigureCanvasTkAgg(fig, master=frame)
        chart.get_tk_widget().pack(fill="both", expand=True)

    def open_add_window(self, edit_activity=None):
        win = ctk.CTkToplevel(self)
        win.title("Gerenciar Registro - Cable")
        win.geometry("520x620")
        win.grab_set()
        
        ctk.CTkLabel(win, text="Nome da Atividade:").pack(pady=(15, 2), padx=20, anchor="w")
        ent_name = ctk.CTkEntry(win, width=420)
        ent_name.pack(padx=20, fill="x")
        
        ctk.CTkLabel(win, text="Tipo Geral:").pack(pady=(10, 2), padx=20, anchor="w")
        cmb_type = ctk.CTkComboBox(win, values=list(RULES.keys()), width=420)
        cmb_type.pack(padx=20, fill="x")
        
        ctk.CTkLabel(win, text="Categoria Específica:").pack(pady=(10, 2), padx=20, anchor="w")
        cmb_sub = ctk.CTkComboBox(win, values=[], width=420)
        cmb_sub.pack(padx=20, fill="x")
        
        def update_subs(choice):
            sub_list = list(RULES[choice]["subs"].keys())
            cmb_sub.configure(values=sub_list)
            cmb_sub.set(sub_list[0])
            
        cmb_type.configure(command=update_subs)
        
        ctk.CTkLabel(win, text="Quantidade de Horas:").pack(pady=(10, 2), padx=20, anchor="w")
        ent_hours = ctk.CTkEntry(win, width=420)
        ent_hours.pack(padx=20, fill="x")
        
        ctk.CTkLabel(win, text="Data Completa (DD/MM/AAAA):").pack(pady=(10, 2), padx=20, anchor="w")
        ent_date = ctk.CTkEntry(win, width=420, placeholder_text="Ex: 05/07/2026")
        ent_date.pack(padx=20, fill="x")
        
        ctk.CTkLabel(win, text="Observações e Localizador de Comprovante:").pack(pady=(10, 2), padx=20, anchor="w")
        txt_obs = ctk.CTkTextbox(win, height=60, width=420)
        txt_obs.pack(padx=20, fill="x")
        
        update_subs(cmb_type.get())
        
        if edit_activity:
            ent_name.insert(0, edit_activity["name"])
            cmb_type.set(edit_activity["type"])
            update_subs(edit_activity["type"])
            cmb_sub.set(edit_activity["category"])
            ent_hours.insert(0, str(edit_activity["hours"]))
            ent_date.insert(0, edit_activity["start_date"])
            txt_obs.insert("0.0", edit_activity["observations"])

        def save():
            try:
                hours = float(ent_hours.get())
            except ValueError:
                messagebox.showerror("Erro", "Insira um número válido para as horas.")
                return
            
            date_str = ent_date.get().strip()
            try:
                datetime.strptime(date_str, "%d/%m/%Y")
            except ValueError:
                messagebox.showerror("Erro de Data", "A data deve estar no formato DD/MM/AAAA válido.")
                return
                
            new_act = {
                "id": edit_activity["id"] if edit_activity else datetime.now().timestamp(),
                "name": ent_name.get(),
                "type": cmb_type.get(),
                "category": cmb_sub.get(),
                "hours": hours,
                "start_date": date_str,
                "observations": txt_obs.get("0.0", "end").strip()
            }
            
            if edit_activity:
                self.activities = [new_act if a["id"] == edit_activity["id"] else a for a in self.activities]
            else:
                self.activities.append(new_act)
                
            save_data(self.activities)
            self.render_dashboard()
            win.destroy()
            
        ctk.CTkButton(win, text="Confirmar Registro", fg_color=AZUL_PADRAO, hover_color=AZUL_HOVER, command=save).pack(pady=20)

    def delete_activity(self, activity):
        if messagebox.askyesno("Excluir", f"Remover definitivamente '{activity['name']}'?"):
            self.activities.remove(activity)
            save_data(self.activities)
            self.render_dashboard()

if __name__ == "__main__":
    app = CableApp()
    app.mainloop()