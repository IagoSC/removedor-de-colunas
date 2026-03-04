# Ferramenta de Anonimização de CSV/DBF

Aplicação desktop em Python para **remover colunas sensíveis por nome de cabeçalho** em arquivos `.csv`, `.txt` (separador `;`) e `.dbf`.

## Visão geral

- Interface gráfica com `customtkinter`
- Detecção de encoding com `chardet`
- Leitura de DBF com `dbfread`
- Saída gerada no mesmo diretório com sufixo `_anonimizado`

---

## Para utilizar

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

## Para contribuir com o projeto

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

### Scripts úteis (automação da distribuição)

Para padronizar o processo, use os scripts em `scripts/`:

1. **Gerar release completa (build + pacote + hash):**

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\New-ReleasePackage.ps1 -Version 1.0.0 -Clean
```

Esse comando:
- gera o executável com PyInstaller;
- cria `release\v1.0.0\anonimizador_de_csv_v1.0.0.exe`;
- inclui `README.md` (e política de dados se existir em `DATA_POLICY.md` ou `SECURITY.md`);
- gera `manifest.json`;
- gera `SHA256SUMS.txt`;
- cria `anonimizador_de_csv_v1.0.0.zip`.

2. **(Opcional) Assinar o executável da release:**

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Set-ReleaseSignature.ps1 -Version 1.0.0 -Thumbprint "SEU_THUMBPRINT"
```

3. **Validar a release (estrutura + hash + assinatura opcional):**

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Test-ReleasePackage.ps1 -Version 1.0.0
```

Para exigir assinatura válida na validação:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Test-ReleasePackage.ps1 -Version 1.0.0 -RequireSignature
```

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
