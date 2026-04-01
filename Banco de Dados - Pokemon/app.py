import json
import os
import customtkinter as ctk
from tkinter import messagebox

# Configurações de Aparência
ctk.set_appearance_mode("light") 
ctk.set_default_color_theme("blue")

# Nome exato do seu arquivo
DB_FILE = "Pokemon.json"

class PokedexApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Gerenciamento Pokémon - Full Stack")
        self.geometry("1100x900") 
        
        self.dados_pokemon = self.carregar_banco()
        self.pokemon_em_edicao = None 
        
        # Variáveis de Paginação
        self.pagina_atual = 0
        self.itens_por_pagina = 5
        self.dados_filtrados = []

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar (Cadastro) ---
        self.sidebar = ctk.CTkScrollableFrame(self, width=300, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.lbl_modo = ctk.CTkLabel(self.sidebar, text="CADASTRO", font=ctk.CTkFont(size=20, weight="bold"), text_color="#32CD32")
        self.lbl_modo.pack(pady=20)
        
        self.ent_nome = self.criar_campo("Nome do Pokémon")
        self.ent_tipo = self.criar_campo("Tipos (separados por vírgula)")
        self.ent_hp = self.criar_campo("HP Base")
        self.ent_ataque = self.criar_campo("Ataque Base")
        self.ent_defesa = self.criar_campo("Defesa Base")
        self.ent_atk_esp = self.criar_campo("Ataque Especial")
        self.ent_def_esp = self.criar_campo("Defesa Especial")
        self.ent_velocidade = self.criar_campo("Velocidade")
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
        self.ent_busca.bind("<KeyRelease>", lambda e: self.resetar_e_atualizar())
        
        self.scroll_cards = ctk.CTkScrollableFrame(self.main_container, label_text="Pokédex Ativa", label_font=("Arial", 20, "bold"), label_text_color="#005B00")
        self.scroll_cards.pack(fill="both", expand=True)

        # Controles de Paginação
        self.pagination_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.pagination_frame.pack(fill="x", pady=10)

        self.btn_prev = ctk.CTkButton(self.pagination_frame, text="◀ Anterior", width=100, command=self.pagina_anterior)
        self.btn_prev.pack(side="left", padx=20)

        self.lbl_paginacao = ctk.CTkLabel(self.pagination_frame, text="Página 1 de 1", font=("Arial", 14, "bold"))
        self.lbl_paginacao.pack(side="left", expand=True)

        self.btn_next = ctk.CTkButton(self.pagination_frame, text="Próxima ▶", width=100, command=self.proxima_pagina)
        self.btn_next.pack(side="right", padx=20)

        self.atualizar_visualizacao()

    def criar_campo(self, placeholder):
        entry = ctk.CTkEntry(self.sidebar, placeholder_text=placeholder)
        entry.pack(fill="x", padx=20, pady=5)
        return entry

    def carregar_banco(self):
        if not os.path.exists(DB_FILE): return []
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                conteudo = json.load(f)
                # Verifica se o JSON é um objeto com a chave "pokemons" ou uma lista direta
                if isinstance(conteudo, dict):
                    return conteudo.get("pokemons", [])
                return conteudo if isinstance(conteudo, list) else []
        except:
            return []

    def salvar_banco(self):
        try:
            with open(DB_FILE, 'w', encoding='utf-8') as f:
                # Salva no formato NoSQL (Objeto raiz com chave pokemons)
                json.dump({"pokemons": self.dados_pokemon}, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Erro de Escrita", f"Não foi possível salvar o arquivo: {e}")

    def processar_salvamento(self):
        try:
            nome_val = self.ent_nome.get().strip()
            if not nome_val:
                messagebox.showwarning("Aviso", "O nome do Pokémon é obrigatório.")
                return

            novo_dado = {
                "nome": nome_val,
                "tipo": [t.strip() for t in self.ent_tipo.get().split(",") if t.strip()],
                "estatisticas_base": {
                    "hp": int(self.ent_hp.get() or 0),
                    "ataque": int(self.ent_ataque.get() or 0),
                    "defesa": int(self.ent_defesa.get() or 0),
                    "ataque_especial": int(self.ent_atk_esp.get() or 0),
                    "defesa_especial": int(self.ent_def_esp.get() or 0),
                    "velocidade": int(self.ent_velocidade.get() or 0)
                },
                "perfil": {
                    "altura": self.ent_altura.get() or "N/A",
                    "peso": self.ent_peso.get() or "N/A",
                    "habilidades": [h.strip() for h in self.ent_habilidades.get().split(",") if h.strip()]
                },
                "evolucao": self.ent_evolucao.get() or "N/A"
            }

            if self.pokemon_em_edicao:
                for i, p in enumerate(self.dados_pokemon):
                    if p.get("nome") == self.pokemon_em_edicao:
                        self.dados_pokemon[i] = novo_dado
                        break
            else:
                self.dados_pokemon.append(novo_dado)

            self.salvar_banco()
            self.resetar_e_atualizar()
            self.limpar_campos()
        except ValueError:
            messagebox.showerror("Erro", "HP, Ataque, Defesa, etc., devem ser números inteiros.")

    def carregar_para_edicao(self, p):
        self.limpar_campos()
        self.pokemon_em_edicao = p.get("nome")
        self.lbl_modo.configure(text="EDIÇÃO", text_color="#68006B")
        self.btn_salvar.configure(text="Atualizar Pokémon", fg_color="#00035F")
        self.btn_cancelar.configure(state="normal")

        self.ent_nome.insert(0, p.get("nome", ""))
        self.ent_tipo.insert(0, ", ".join(p.get("tipo", [])))
        
        stats = p.get("estatisticas_base", {})
        self.ent_hp.insert(0, stats.get("hp", 0))
        self.ent_ataque.insert(0, stats.get("ataque", 0))
        self.ent_defesa.insert(0, stats.get("defesa", 0))
        self.ent_atk_esp.insert(0, stats.get("ataque_especial", 0))
        self.ent_def_esp.insert(0, stats.get("defesa_especial", 0))
        self.ent_velocidade.insert(0, stats.get("velocidade", 0))
        
        perfil = p.get("perfil", {})
        self.ent_altura.insert(0, perfil.get("altura", ""))
        self.ent_peso.insert(0, perfil.get("peso", ""))
        self.ent_habilidades.insert(0, ", ".join(perfil.get("habilidades", [])))
        self.ent_evolucao.insert(0, p.get("evolucao", ""))

    def criar_card(self, p):
        # Uso extensivo de .get() para evitar KeyError se o JSON estiver incompleto
        nome = p.get("nome", "Desconhecido").upper()
        tipos = " / ".join(p.get("tipo", ["???"]))
        stats = p.get("estatisticas_base", {})
        perfil = p.get("perfil", {})
        
        card = ctk.CTkFrame(self.scroll_cards, border_width=2, border_color="#00FFFF", fg_color="white")
        card.pack(fill="x", pady=10, padx=10)
        
        header = ctk.CTkFrame(card, fg_color="#f0f0f0")
        header.pack(fill="x")
        
        ctk.CTkLabel(header, text=nome, font=ctk.CTkFont(size=16, weight="bold"), text_color="#32CD32").pack(side="left", padx=10)
        
        btn_del = ctk.CTkButton(header, text="X", width=30, height=20, fg_color="#FF4500", command=lambda: self.deletar_pokemon(p.get("nome")))
        btn_del.pack(side="right", padx=5, pady=5)
        
        btn_edit = ctk.CTkButton(header, text="✏️", width=30, height=20, fg_color="#00FFFF", text_color="black", command=lambda: self.carregar_para_edicao(p))
        btn_edit.pack(side="right", padx=5, pady=5)

        info = (f"Tipos: {tipos}\n"
                f"Status: HP: {stats.get('hp',0)} | ATK: {stats.get('ataque',0)} | DEF: {stats.get('defesa',0)} | SPD: {stats.get('velocidade',0)}\n"
                f"Perfil: Altura: {perfil.get('altura','-')} | Peso: {perfil.get('peso','-')}\n"
                f"Evolução: {p.get('evolucao', 'N/A')}")
        
        ctk.CTkLabel(card, text=info, justify="left", font=("Consolas", 12)).pack(padx=10, pady=10, anchor="w")

    def deletar_pokemon(self, nome_poke):
        if messagebox.askyesno("Confirmar", f"Excluir {nome_poke}?"):
            self.dados_pokemon = [p for p in self.dados_pokemon if p.get("nome") != nome_poke]
            self.salvar_banco()
            self.resetar_e_atualizar()

    def resetar_e_atualizar(self):
        self.pagina_atual = 0
        self.atualizar_visualizacao()

    def atualizar_visualizacao(self):
        for w in self.scroll_cards.winfo_children(): w.destroy()
        
        termo = self.ent_busca.get().lower()
        self.dados_filtrados = [
            p for p in self.dados_pokemon 
            if termo in str(p.get("nome", "")).lower() or any(termo in str(t).lower() for t in p.get("tipo", []))
        ]

        total_itens = len(self.dados_filtrados)
        total_paginas = max(1, (total_itens + self.itens_por_pagina - 1) // self.itens_por_pagina)

        if self.pagina_atual >= total_paginas: self.pagina_atual = total_paginas - 1

        inicio = self.pagina_atual * self.itens_por_pagina
        fim = inicio + self.itens_por_pagina
        
        for p in self.dados_filtrados[inicio:fim]:
            self.criar_card(p)

        self.lbl_paginacao.configure(text=f"Página {self.pagina_atual + 1} de {total_paginas} ({total_itens} Pokémons)")
        self.btn_prev.configure(state="normal" if self.pagina_atual > 0 else "disabled")
        self.btn_next.configure(state="normal" if fim < total_itens else "disabled")

    def proxima_pagina(self):
        self.pagina_atual += 1
        self.atualizar_visualizacao()

    def pagina_anterior(self):
        self.pagina_atual -= 1
        self.atualizar_visualizacao()

    def limpar_campos(self):
        self.pokemon_em_edicao = None
        self.lbl_modo.configure(text="CADASTRO", text_color="#32CD32")
        self.btn_salvar.configure(text="Salvar Pokémon", fg_color="#32CD32")
        self.btn_cancelar.configure(state="disabled")
        for widget in self.sidebar.winfo_children():
            if isinstance(widget, ctk.CTkEntry): widget.delete(0, 'end')

if __name__ == "__main__":
    PokedexApp().mainloop()
