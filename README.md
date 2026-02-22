# Card Bug Generator

Um aplicativo desktop focado em padronizar e agilizar a criação de Bug Reports. Utiliza a IA do Google Gemini para transformar anotações rápidas em documentação técnica estruturada e pronta para o Jira/Azure DevOps.

## Funcionalidades

* **Refinamento Inteligente:** A IA organiza seu rascunho nos padrões técnicos de QA (Comportamento Atual, Esperado, Passos para Replicar).
* **Análise de Impacto:** Gera automaticamente um bloco de resumo de impacto do bug para documentação.
* **Ações Rápidas:** Copie o card final com um clique ou exporte diretamente para PDF.

---

## Como Instalar e Rodar

1. **Faça o clone do repositório e acesse a pasta:**
   ```bash
   git clone https://github.com/Patrickscv/card-bug-generator.git
   cd card-bug-generator
   ```

2. **Instale as dependências do projeto:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure a sua API Key:**
   * Crie um arquivo chamado `.env` na raiz do projeto (use o `.env.example` como base).
   * Insira a sua chave do Google AI Studio dentro dele, neste formato:
     ```env
     GEMINI_API_KEY=sua_chave_aqui
     ```

4. **Inicie o aplicativo:**
   ```bash
   python src/card_generator.py
   ```
