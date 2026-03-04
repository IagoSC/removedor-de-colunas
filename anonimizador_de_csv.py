from io import TextIOWrapper
import chardet
import customtkinter as ctk
from tkinter import filedialog
import os
from dbfread import DBF

# --- Configuração da interface visual ---
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class HeaderMatcherApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuração layout de janela
        self.title("Ferramenta de anonimização de dados")
        self.geometry("600x600") 
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1) 

        # --- Seção de Seleção de Arquivo (Layout Linha 0) ---
        self.file_path = None
        
        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        self.btn_browse = ctk.CTkButton(self.file_frame, text="Selecione o arquivo CSV", command=self.browse_file)
        self.btn_browse.pack(side="left", padx=10, pady=10)
        
        self.lbl_filename = ctk.CTkLabel(self.file_frame, text="Nenhum arquivo selecionado", text_color="gray")
        self.lbl_filename.pack(side="left", padx=10)

        self.lbl_instruction = ctk.CTkLabel(self, text="Cole a lista de cabeçalhos a serem encontrados (um por linha):", anchor="w")
        self.lbl_instruction.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="w")

        self.txt_input = ctk.CTkTextbox(self, height=120)
        self.txt_input.grid(row=3, column=0, padx=20, pady=(5, 10), sticky="ew")

        self.btn_process = ctk.CTkButton(self, text="Anonimizar", command=self.process_data, height=40)
        self.btn_process.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        self.lbl_output = ctk.CTkLabel(self, text="Results:", anchor="w")
        self.lbl_output.grid(row=5, column=0, padx=20, pady=(10, 0), sticky="w")

        self.txt_output = ctk.CTkTextbox(self, state="disabled", height=150)
        self.txt_output.grid(row=6, column=0, padx=20, pady=(5, 20), sticky="nsew")

        # Configure text tags for coloring messages
        self.txt_output._textbox.tag_configure("normal", foreground="gray")
        self.txt_output._textbox.tag_configure("warn", foreground="orange")
        self.txt_output._textbox.tag_configure("error", foreground="red")
        self.txt_output._textbox.tag_configure("success", foreground="green")

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self, mode="determinate")
        self.progress_bar.set(0)
        self.progress_bar.grid(row=7, column=0, padx=20, pady=(0, 20), sticky="ew")

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Selecione arquivo",
            filetypes=(("All files", "*.*"), ("Text/CSV files", "*.txt *.csv"), ("DBF files", "*.dbf *.DBF"))
        )
        if filename:
            self.file_path = filename
            self.log_output(f"Arquivo selecionado: {filename}", "success")
            self.lbl_filename.configure(text=os.path.basename(filename), text_color=("black", "white"))
            detect_encoding = chardet.detect(open(filename, 'rb').read(100_000)) # Detecta enconding utilizando apenas os primeiros 100KB do arquivo
            self.file_encoding = detect_encoding['encoding']
            self.log_output(f"Encoding de arquivo detectado: {detect_encoding['encoding']}. Confiança {detect_encoding['confidence']}")
            if detect_encoding['confidence'] < 0.65:
                self.log_output(f"Confiança baixa na detecção de encoding. ({detect_encoding['confidence']*100:.2f}%)", "warn")
                self.log_output(f"Baixa confiança no formato de enconding do arquivo pode causar erros na leitura.", "warn")
                self.log_output(f"Arquivos com caracteres especiais podem ser afetados.", "warn")
            self.extension = os.path.splitext(filename)[1].lower()

    def count_lines(self, file_path: str) -> int:
        with open(file_path, 'r', encoding=self.file_encoding) as f:  # Use the detected encoding if available
            self.file_lines = sum(1 for _ in f)

    def handle_headers(self, headers: list[str], target_strings: list[str]):
        self.total_columns = len(headers)
        self.log_output(f"\n\nAnalizando cabeçalho (separador: ' ; ')")
        self.log_output(f"Total de colunas no arquivo: {self.total_columns}")
        self.log_output("-" * 50 + "\n")
        self.column_idxs = []
        for target in self.target_columns:
            try:
                index = headers.index(target)
                self.column_idxs.append(index)
            except ValueError:
                self.log_output(f"COLUNA NÃO ENCONTRADA: '{target}'", "warn")
        if len(self.column_idxs) == 0:
            self.log_output("NENHUMA COLUNA FOI ENCONTRADA PARA REMOÇÃO.", "error")
            raise Exception("Sytem Error: Nenhuma coluna foi encontrada para remoção.")
        else:
            self.log_output(f"{len(self.column_idxs)} Colunas encontradas")
            new_file = open(self.new_file_name, 'w', encoding=self.file_encoding)
            line_index = 1
            new_headers = self.remove_columns_from_row(headers, self.column_idxs, len(headers), line_index)
            new_file.write(new_headers)
            return new_file

    def handle_row(self, new_file, record: list[str], line_index: int =0):
        new_line = self.remove_columns_from_row(record, self.column_idxs, self.total_columns, line_index)
        new_file.write(new_line)
        if(line_index % 100 == 0):
            progress_bar_value = line_index / self.file_lines
            self.progress_bar.set(progress_bar_value)

    def process_data(self):
        if(not self.file_path or not self.extension):
            self.clear_log_output("Selecione um arquivo primeiro.", "error")
            return       
                
        self.clear_log_output("Iniciando processo de anonimização...", "normal")
        
        raw_input = self.txt_input.get("1.0", "end")
        if not raw_input.strip():
            self.clear_log_output("Nenhum cabeçalho fornecido.", "error")
            return

        self.target_columns = [line.strip() for line in raw_input.split('\n') if line.strip()]
        self.new_file_name = self.create_new_filename(self.file_path)

        if self.extension == '.csv' or self.extension == '.txt':
            self.process_csv()
        elif self.extension == '.dbf':
            self.process_dbf()
        else: 
            self.log_output(f"Formato de arquivo {self.extension} não suportado no momento.", "error")
            return
        self.log_output("\n\n\n")
        self.log_output(f"Arquivo anonimizado criado: {self.new_file_name}", "success")
    
    def process_dbf(self):
        table = DBF(self.file_path, encoding=self.file_encoding)
        self.file_lines = table._count_records()
        new_file = None
        try:
            new_file = self.handle_headers(table.field_names, self.target_columns)
            for index, record in enumerate(table.records):
                self.handle_row(new_file, list(record.values()), index)  # +2 para considerar o cabeçalho e índice começando em 0
        except Exception as e:
            os.remove(self.new_file_name)  # Remove o arquivo criado em caso de erro
            self.log_output(f"Finalizando Processo", "error")
        if(new_file):
            new_file.close()

    def process_csv(self):
        try:
            self.count_lines(self.file_path)

            with open(self.file_path, 'r', encoding=self.file_encoding) as f:
                first_line = f.readline()
                file_headers = first_line.strip().split(';')
                new_file = None
                try:
                    new_file = self.handle_headers(file_headers, self.target_columns)
                    if new_file:
                        line_index = 1
                        while read_line := f.readline():
                            line_index += 1
                            self.handle_row(new_file, read_line.strip().split(';'), line_index)
                except Exception as e:
                    os.remove(self.new_file_name)  # Remove o arquivo criado em caso de erro
                    self.log_output(f"System Error: Finalizando Processo", "error")
                if new_file:
                        new_file.close()

        except Exception as e:
            self.log_output(f"System Error: {str(e)}", "error")

    def clear_log_output(self, message, state="error"):
        self.txt_output.configure(state="normal")
        self.txt_output.delete("1.0", "end")
        self.txt_output._textbox.insert("1.0", message+"\n", state)
        self.txt_output.configure(state="disabled")

    def log_output(self, message, state="normal"):
        if(state == "warn"):
            message = "ATENÇÃO - " + message
        if(state == "error"):
            message = "ERRO - " + message
        self.txt_output.configure(state="normal")
        self.txt_output._textbox.insert("end", message+"\n", state)
        self.txt_output.configure(state="disabled")

    def remove_columns_from_row(self, columns: list[str], column_indexes: list[int], total_columns: int, row_index: int) -> str:
        if(len(columns) != total_columns):
            columns += [''] * (total_columns - len(columns))
            self.log_output(f"Linha ({row_index}) com número inesperado de colunas detectada. Esperado: {total_columns}, Encontrado: {len(columns)}", "warn")
            raise Exception("System Error: Linha com número inesperado de colunas detectada.")
        for index in column_indexes:

            del columns[index]
        return ';'.join(columns) + '\n'

    def create_new_filename(self, original_path: str) -> str:
        base, ext = os.path.splitext(original_path)
        new_file_name = f"{base}_anonimizado{ext}"
        counter = 1
        while os.path.exists(new_file_name):
            new_file_name = f"{base}_anonimizado({counter}){ext}"
            counter += 1
        return new_file_name

if __name__ == "__main__":
    app = HeaderMatcherApp()
    app.mainloop()