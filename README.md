# Ferramenta de Anonimização de CSV/DBF

Aplicação desktop em Python para **remover colunas sensíveis por nome de cabeçalho** em arquivos `.csv`, `.txt` (separador `;`) e `.dbf`.

## Visão geral

- Interface gráfica com `customtkinter`
- Detecção de encoding com `chardet`
- Leitura de DBF com `dbfread`
- Saída gerada no mesmo diretório com sufixo `_anonimizado`

---

## Como usar

1. Execute o programa.
2. Clique em **Selecione o arquivo CSV** (também aceita TXT e DBF).
3. Cole os cabeçalhos a remover, **um por linha**.
4. Clique em **Anonimizar**.
5. O novo arquivo será criado automaticamente (ex.: `dados_anonimizado.csv`).

### Regras importantes de formato

- Para CSV/TXT, o separador esperado é `;`.
- Os nomes dos cabeçalhos devem corresponder exatamente ao arquivo.
- Em caso de linhas com quantidade inesperada de colunas, o processo pode ser interrompido para evitar saída inconsistente.

---

## Como buildar

### Pré-requisitos

- Python 3.10+ (recomendado)
- `pip`

### 1) Instalar dependências

```bash
pip install customtkinter chardet dbfread pyinstaller
```

### 2) Rodar em modo desenvolvimento

```bash
python anonimizador_de_csv.py
```

### 3) Gerar executável (Windows)

```bash
pyinstaller --onefile --windowed anonimizador_de_csv.py
```

Saída esperada:

- Executável em `dist/anonimizador_de_csv.exe`

---

## Distribuição

Opções comuns de distribuição:

1. **Distribuir apenas o `.exe`** (`dist/anonimizador_de_csv.exe`) para usuários Windows.
2. Publicar uma release interna (rede corporativa, SharePoint, GitHub Releases, etc.).
3. Incluir um pacote com:
   - executável
   - README
   - política de uso de dados (quando aplicável)

Boas práticas de distribuição:

- Versionar builds (ex.: `anonimizador_de_csv_v1.2.0.exe`).
- Assinar digitalmente o binário quando possível.
- Manter checksum (SHA-256) para validação de integridade.

---

## Segurança e privacidade (data privacy/compliance)

Esta ferramenta **remove colunas**, mas não garante anonimização total em todos os cenários.

### Pontos de atenção

- **Risco de reidentificação**: mesmo sem identificadores diretos, combinação de campos pode identificar pessoas.
- **Dados sensíveis remanescentes**: informações pessoais podem existir em colunas não removidas.
- **Arquivos temporários e cópias**: versões originais e intermediárias podem permanecer em disco/backups.
- **Vazamento por distribuição**: envio por e-mail, cloud pública ou pasta compartilhada sem controle pode expor dados.

### Recomendações mínimas

- Classificar o dataset antes do processamento.
- Definir e revisar lista de colunas sensíveis com área jurídica/compliance.
- Processar preferencialmente em máquina/ambiente controlado.
- Criptografar disco e diretórios de trabalho quando possível.
- Aplicar controle de acesso aos arquivos de entrada e saída.
- Definir política de retenção e descarte seguro dos dados originais.
- Validar aderência à legislação aplicável (ex.: LGPD, políticas internas).

> Observação: em contextos regulados, anonimização pode exigir técnicas adicionais (generalização, mascaramento, supressão contextual, k-anonimato, etc.) e validação formal.

---

## Casos de uso

- Compartilhar bases para análise sem expor identificadores diretos.
- Preparar dados para treinamento interno e demonstrações.
- Reduzir dados sensíveis antes de envio para fornecedores.
- Criar versões minimizadas para testes de software.

---

## Como portar

### Portar para Linux/macOS

- O código é Python e tende a funcionar com ajustes mínimos.
- Instalar as mesmas dependências via `pip`.
- Executar:

```bash
python anonimizador_de_csv.py
```

- Para empacotar em cada SO, gere build no próprio sistema alvo com PyInstaller.

### Portar para CLI (sem interface)

Passos sugeridos:

1. Extrair a lógica de processamento para funções puras (leitura, mapeamento de colunas, escrita).
2. Criar parser de argumentos (`argparse`) para:
   - arquivo de entrada
   - colunas a remover
   - caminho de saída
3. Reutilizar validações e logs para execução automatizada em pipelines.

---

## Exemplo pequeno

Entrada (`pacientes.csv`):

```csv
nome;cpf;idade;cidade
Ana;11122233344;34;Recife
Bruno;99988877766;29;Olinda
```

Cabeçalhos informados na interface (um por linha):

```text
nome
cpf
```

Saída (`pacientes_anonimizado.csv`):

```csv
idade;cidade
34;Recife
29;Olinda
```

---

## Limitações atuais

- CSV/TXT com separador diferente de `;` não são tratados automaticamente.
- A remoção depende de correspondência exata de cabeçalho.
- O processo atual remove colunas; não faz mascaramento parcial de valores.
