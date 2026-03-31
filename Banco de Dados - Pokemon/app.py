import json
import os
import customtkinter as ctk
from tkinter import messagebox

# Configurações de Aparência
ctk.set_appearance_mode("light") 
ctk.set_default_color_theme("blue")

DB_FILE = "pokemon.json"

class PokedexApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Gerenciamento Pokémon")
        self.geometry("1100x850") # Aumentado para acomodar mais campos
        
        self.dados_pokemon = self.carregar_banco()
        self.pokemon_em_edicao = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar = ctk.CTkScrollableFrame(self, width=300, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.lbl_modo = ctk.CTkLabel(self.sidebar, text="CADASTRO", font=ctk.CTkFont(size=20, weight="bold"), text_color="#32CD32")
        self.lbl_modo.pack(pady=20)
        
        self.ent_nome = self.criar_campo("Nome do Pokémon")
        self.ent_tipo = self.criar_campo("Tipos (separados por vírgula)")
        
        # Status Base
        self.ent_hp = self.criar_campo("HP Base")
        self.ent_ataque = self.criar_campo("Ataque Base")
        self.ent_defesa = self.criar_campo("Defesa Base")
        self.ent_atk_esp = self.criar_campo("Ataque Especial")
        self.ent_def_esp = self.criar_campo("Defesa Especial")
        self.ent_velocidade = self.criar_campo("Velocidade")
        
        # Perfil
        self.ent_altura = self.criar_campo("Altura (ex: 0.7 m)")
        self.ent_peso = self.criar_campo("Peso (ex: 6.9 kg)")
        self.ent_habilidades = self.criar_campo("Habilidades (vírgula)")
        self.ent_evolucao = self.criar_campo("Próxima Evolução")

        self.btn_salvar = ctk.CTkButton(self.sidebar, text="Salvar Pokémon", fg_color="#32CD32", hover_color="#228B22", command=self.processar_salvamento)
        self.btn_salvar.pack(pady=10, padx=20)

        self.btn_cancelar = ctk.CTkButton(self.sidebar, text="Cancelar Edição", fg_color="gray", command=self.limpar_campos, state="disabled")
        self.btn_cancelar.pack(pady=5, padx=20)

        # --- Área Principal ---
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self.search_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.search_frame.pack(fill="x", pady=(0, 20))
        
        self.ent_busca = ctk.CTkEntry(self.search_frame, placeholder_text="Buscar por nome ou tipo...", width=400)
        self.ent_busca.pack(side="left", padx=(0, 10))
        self.ent_busca.bind("<KeyRelease>", lambda e: self.atualizar_visualizacao())
        
        self.scroll_cards = ctk.CTkScrollableFrame(self.main_container, label_text="Pokédex Ativa", label_font=("Arial", 20, "bold"), label_text_color="#005B00")
        self.scroll_cards.pack(fill="both", expand=True)

        self.atualizar_visualizacao()

    def criar_campo(self, placeholder):
        entry = ctk.CTkEntry(self.sidebar, placeholder_text=placeholder)
        entry.pack(fill="x", padx=20, pady=5)
        return entry

    def carregar_banco(self):
        if not os.path.exists(DB_FILE): return []
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f: return json.load(f)
        except: return []

    def salvar_banco(self):
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.dados_pokemon, f, indent=2, ensure_ascii=False)

    def processar_salvamento(self):
        try:
            novo_dado = {
                "nome": self.ent_nome.get(),
                "tipo": [t.strip() for t in self.ent_tipo.get().split(",")],
                "estatisticas_base": {
                    "hp": int(self.ent_hp.get()),
                    "ataque": int(self.ent_ataque.get()),
                    "defesa": int(self.ent_defesa.get()),
                    "ataque_especial": int(self.ent_atk_esp.get()),
                    "defesa_especial": int(self.ent_def_esp.get()),
                    "velocidade": int(self.ent_velocidade.get())
                },
                "perfil": {
                    "altura": self.ent_altura.get(),
                    "peso": self.ent_peso.get(),
                    "habilidades": [h.strip() for h in self.ent_habilidades.get().split(",")]
                },
                "evolucao": self.ent_evolucao.get()
            }

            if self.pokemon_em_edicao is not None:
                for i, p in enumerate(self.dados_pokemon):
                    if p["id"] == self.pokemon_em_edicao:
                        novo_dado["id"] = self.pokemon_em_edicao
                        self.dados_pokemon[i] = novo_dado
                        break
            else:
                novo_dado["id"] = max([p.get("id", 0) for p in self.dados_pokemon], default=0) + 1
                self.dados_pokemon.append(novo_dado)

            self.salvar_banco()
            self.atualizar_visualizacao()
            self.limpar_campos()
        except ValueError:
            messagebox.showerror("Erro", "Certifique-se de que todos os campos de status são números.")

    def carregar_para_edicao(self, p):
        self.limpar_campos()
        self.pokemon_em_edicao = p["id"]
        self.lbl_modo.configure(text="EDIÇÃO", text_color="#68006B")
        self.btn_salvar.configure(text="Atualizar Pokémon", fg_color="#00035F", hover_color="#00CED1")
        self.btn_cancelar.configure(state="normal")

        # Preenchimento Completo
        self.ent_nome.insert(0, p["nome"])
        self.ent_tipo.insert(0, ", ".join(p["tipo"]))
        self.ent_hp.insert(0, p["estatisticas_base"]["hp"])
        self.ent_ataque.insert(0, p["estatisticas_base"]["ataque"])
        self.ent_defesa.insert(0, p["estatisticas_base"]["defesa"])
        self.ent_atk_esp.insert(0, p["estatisticas_base"].get("ataque_especial", 0))
        self.ent_def_esp.insert(0, p["estatisticas_base"].get("defesa_especial", 0))
        self.ent_velocidade.insert(0, p["estatisticas_base"].get("velocidade", 0))
        self.ent_altura.insert(0, p["perfil"]["altura"])
        self.ent_peso.insert(0, p["perfil"]["peso"])
        self.ent_habilidades.insert(0, ", ".join(p["perfil"].get("habilidades", [])))
        self.ent_evolucao.insert(0, p.get("evolucao", ""))

    def criar_card(self, p):
        card = ctk.CTkFrame(self.scroll_cards, border_width=2, border_color="#00FFFF", fg_color="white")
        card.pack(fill="x", pady=10, padx=10)
        
        header = ctk.CTkFrame(card, fg_color="#f0f0f0", corner_radius=0)
        header.pack(fill="x")
        
        ctk.CTkLabel(header, text=p["nome"].upper(), font=ctk.CTkFont(size=16, weight="bold"), text_color="#32CD32").pack(side="left", padx=10)
        
        btn_del = ctk.CTkButton(header, text="X", width=30, height=20, fg_color="#FF4500", command=lambda: self.deletar_pokemon(p["id"]))
        btn_del.pack(side="right", padx=5, pady=5)
        
        btn_edit = ctk.CTkButton(header, text="✏️", width=30, height=20, fg_color="#00FFFF", text_color="black", command=lambda: self.carregar_para_edicao(p))
        btn_edit.pack(side="right", padx=5, pady=5)

        # Montagem dos dados detalhados
        eb = p['estatisticas_base']
        pf = p['perfil']
        
        linha1 = f"Tipos: {' / '.join(p['tipo'])}"
        linha2 = f"Status: HP: {eb['hp']} | ATK: {eb['ataque']} | DEF: {eb['defesa']} | SATK: {eb.get('ataque_especial', '-')} | SDEF: {eb.get('defesa_especial', '-')} | SPD: {eb.get('velocidade', '-')}"
        linha3 = f"Perfil: Altura: {pf['altura']} | Peso: {pf['peso']}"
        linha4 = f"Habilidades: {', '.join(pf.get('habilidades', ['N/A']))}"
        linha5 = f"Evolução: {p.get('evolucao', 'N/A')}"
        
        info_completa = f"{linha1}\n{linha2}\n{linha3}\n{linha4}\n{linha5}"
        
        ctk.CTkLabel(card, text=info_completa, justify="left", font=("Consolas", 12)).pack(padx=10, pady=10, anchor="w")

    def deletar_pokemon(self, id_poke):
        if messagebox.askyesno("Confirmar", "Deseja excluir este Pokémon?"):
            self.dados_pokemon = [p for p in self.dados_pokemon if p["id"] != id_poke]
            self.salvar_banco()
            self.atualizar_visualizacao()

    def atualizar_visualizacao(self):
        for w in self.scroll_cards.winfo_children(): w.destroy()
        termo = self.ent_busca.get().lower()
        for p in self.dados_pokemon:
            if termo in p["nome"].lower() or any(termo in t.lower() for t in p["tipo"]):
                self.criar_card(p)

    def limpar_campos(self):
        self.pokemon_em_edicao = None
        self.lbl_modo.configure(text="CADASTRO", text_color="#32CD32")
        self.btn_salvar.configure(text="Salvar Pokémon", fg_color="#32CD32")
        self.btn_cancelar.configure(state="disabled")
        # Limpa todos os campos dinamicamente
        for widget in self.sidebar.winfo_children():
            if isinstance(widget, ctk.CTkEntry):
                widget.delete(0, 'end')

if __name__ == "__main__":
    PokedexApp().mainloop()
