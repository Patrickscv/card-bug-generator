import os
from dotenv import load_dotenv
import customtkinter as ctk
from google import genai
import pyperclip
from tkinter import messagebox, filedialog
from fpdf import FPDF

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("ERRO: GEMINI_API_KEY não encontrada no arquivo .env")
    client = None
else:
    client = genai.Client(api_key=API_KEY)

TEMPLATE_INPUT = """
Comportamento Atual (O que acontece):

Comportamento Esperado (O que deveria acontecer): 

Passos para Replicar:

"""

PROMPT_SISTEMA = """
Você é um QA Automation Engineer especializado em documentação técnica. 
Ao gerar a resposta, forneça apenas os dados pedidos nos passos abaixo, mais nada.
Sua tarefa é REESCREVER e REFINAR o bug report fornecido, seguindo esta estrutura:

Título: Descrição curta do erro (ex: Falha de validação ou Erro de Layout)

Comportamento Atual:
---
[Descreva o problema de forma clara].

Comportamento Esperado:
---
[Descreva a regra de negócio correta].

Passos para Replicar:
---
1. Acesse o caminho [Caminho do Menu].
2. Realize a ação [Ação 1].
3. Realize a ação [Ação 2].
4. Verifique: [O ponto exato onde o erro se manifesta].

Evidências: [Local reservado para anexos/prints]

---
RESUMO DE IMPACTO (Para documentos):
Regras para esta seção:
1. Início: Fale brevemente o que é o card (ex: "Correção no botão...", "Remoção da regra...").
2. Estrutura de Impacto: Use o formato: "Possível impacto em [Módulo/Tela], podendo ocasionar erros ao [ação específica]".
3. Casos sem Erro: Se não houver impacto, finalize com: "Nenhum impacto aparente."
4. Estética: Texto limpo, sem sombreamento ou blocos de código.
"""

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class CardGeneratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Gerador de Cards")
        self.geometry("1000x980")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((3, 6), weight=1) 

        self.title_help = ctk.CTkLabel(self, text="📖 GUIA DE PREENCHIMENTO:", font=ctk.CTkFont(size=14, weight="bold"), text_color="#aaaaaa")
        self.title_help.grid(row=0, column=0, padx=30, pady=(20, 0), sticky="w")

        self.help_frame = ctk.CTkFrame(self, fg_color="#1e1e1e", border_width=1, border_color="#3d3d3d")
        self.help_frame.grid(row=1, column=0, padx=30, pady=(5, 15), sticky="ew")
        
        guid_text = (
            "• COMPORTAMENTO ATUAL: Descreva o bug e logs de erro.\n\n"
            "• COMPORTAMENTO ESPERADO: Como o sistema deve agir?\n\n"
            "• PASSOS PARA REPLICAR: Especifique o caminho para replicar o Bug, seguindo o padrão tela>funcionalidade>ação."
        )
        
        self.label_help = ctk.CTkLabel(self.help_frame, text=guid_text, justify="left", anchor="w", font=ctk.CTkFont(size=13), text_color="#bbbbbb")
        self.label_help.pack(padx=20, pady=15, fill="x")

        self.title_input = ctk.CTkLabel(self, text="📝 RASCUNHO DO CARD:", font=ctk.CTkFont(size=14, weight="bold"), text_color="#aaaaaa")
        self.title_input.grid(row=2, column=0, padx=30, pady=(5, 0), sticky="w")

        self.input_text = ctk.CTkTextbox(self, height=250, font=ctk.CTkFont(size=14), border_width=2)
        self.input_text.grid(row=3, column=0, padx=30, pady=(5, 10), sticky="nsew")
        self.input_text.insert("1.0", TEMPLATE_INPUT)

        self.btn_generate = ctk.CTkButton(self, text="GERAR O CARD", height=55, command=self.process_ai, font=ctk.CTkFont(size=15, weight="bold"))
        self.btn_generate.grid(row=4, column=0, padx=30, pady=15, sticky="ew")

        self.title_output = ctk.CTkLabel(self, text="✨ CARD REFINADO PELA IA:", font=ctk.CTkFont(size=14, weight="bold"), text_color="#57bb8a")
        self.title_output.grid(row=5, column=0, padx=30, pady=(5, 0), sticky="w")

        self.output_text = ctk.CTkTextbox(self, height=250, fg_color="#000000", text_color="#57bb8a", font=ctk.CTkFont(family="Consolas", size=13))
        self.output_text.grid(row=6, column=0, padx=30, pady=(5, 15), sticky="nsew")

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=7, column=0, padx=30, pady=(0, 30), sticky="ew")
        self.button_frame.grid_columnconfigure((0, 1), weight=1)

        self.btn_copy = ctk.CTkButton(
            self.button_frame, 
            text="COPIAR", 
            width=150,
            height=35,
            corner_radius=20, 
            fg_color="#28a745", 
            hover_color="#218838", 
            command=self.copy_content,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.btn_copy.grid(row=0, column=0, padx=(0, 10), sticky="e")

        self.btn_pdf = ctk.CTkButton(
            self.button_frame, 
            text="📄 GERAR PDF", 
            width=150,
            height=35,
            corner_radius=20, 
            fg_color="#dc3545", 
            hover_color="#c82333", 
            command=self.export_pdf,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.btn_pdf.grid(row=0, column=1, padx=(10, 0), sticky="w")

    def process_ai(self):
        if not client:
            messagebox.showerror("Erro", "API Key não configurada ou inválida.")
            return

        user_content = self.input_text.get("1.0", "end-1c").strip()
        if len(user_content) < 20:
            messagebox.showwarning("Aviso", "Conteúdo muito curto.")
            return

        self.btn_generate.configure(state="disabled", text="GERANDO O CARD...")
        self.update()

        try:
            full_prompt = f"{PROMPT_SISTEMA}\n\nCONTEÚDO PARA REFINAR:\n{user_content}"
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=full_prompt
            )
            
            self.output_text.delete("1.0", "end")
            self.output_text.insert("1.0", response.text)
        except Exception as e:
            messagebox.showerror("Erro Crítico", f"Falha na comunicação: {str(e)}")
        finally:
            self.btn_generate.configure(state="normal", text="GERAR O CARD")

    def copy_content(self):
        content = self.output_text.get("1.0", "end-1c")
        if content and "aparecerá aqui" not in content:
            pyperclip.copy(content)
            messagebox.showinfo("Sucesso", "Copiado para a área de transferência!")

    def export_pdf(self):
        content = self.output_text.get("1.0", "end-1c")
        if not content or "aparecerá aqui" in content:
            messagebox.showwarning("Aviso", "Gere um card antes de exportar.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if file_path:
            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.multi_cell(0, 10, content.encode('latin-1', 'replace').decode('latin-1'))
                pdf.output(file_path)
                messagebox.showinfo("Sucesso", "PDF gerado com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao gerar PDF: {e}")

if __name__ == "__main__":
    app = CardGeneratorApp()
    app.mainloop()