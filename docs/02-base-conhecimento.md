# Base de Conhecimento

## Dados Utilizados

Os dados foram arquitetados para simular cenários de "sujeira" real (duplicidades, categorização ambígua) e para testar a segurança das recomendações financeiras.

| Arquivo | Formato | Utilização no Agente |
|---------|---------|---------------------|
| `transacoes_treino.csv` | CSV | Simula o extrato bancário para testes de categorização, detecção de anomalias (duplicidade) e cálculo de fluxo de caixa. |
| `perfis_usuarios.json` | JSON | Contém os arquétipos (`foco_divida`, `foco_reserva`, `foco_controle`) que definem as regras de comportamento e tom de voz do agente. |
| `produtos_financeiros.json` | JSON | Catálogo de investimentos curado com travamento de segurança (`perfis_compativeis`) para evitar sugestões inadequadas. |
| `dataset_intents_treino.csv` | CSV | Pares de perguntas/respostas usados para *Few-Shot Prompting*, ensinando o tom "Casual/Mentor" ao modelo. |


---

## Adaptações nos Dados

Para garantir que o agente fosse realmente "inteligente" e seguro, os dados mockados sofreram as seguintes adaptações estratégicas:

1.  **Injeção de "Armadilhas" no CSV de Transações:**
    * Inserção proposital de transações duplicadas (ex: Apple Services cobrado 2x no mesmo dia) para testar a proatividade do agente.
    * Criação da flag `tipo: transferencia` para garantir que pagamentos de fatura não sejam somados duplamente como despesa.
    * Variação de preços em recorrencias (ex: Netflix mais cara que a média) para gatilho de alertas de inflação pessoal.

2.  **Lógica de Negócio nos JSONs de Perfil:**
    * Em vez de apenas dados cadastrais, adicionamos campos de *Regra de Conduta* (ex: `"bloquear_sugestao_lazer": true` para endividados).
    * Criação de métricas calculadas prévias, como `saldo_livre_real` (Saldo Banco - Contas a Pagar), para dar contexto real ao LLM.

3.  **Trava de Segurança nos Produtos:**
    * Adição do campo `perfis_compativeis` no catálogo de investimentos. Isso permite filtrar via código (Python) o que pode ser enviado ao prompt, impedindo que o LLM alucine recomendando Renda Variável para um perfil conservador/endividado.
---

## Estratégia de Integração

### Como os dados são carregados?
A arquitetura segue um modelo híbrido de **Carregamento em Memória** (para prototipagem rápida no Streamlit) e **Filtragem Pré-Prompt**:

1.  **Inicialização:** Ao iniciar a sessão, o Pandas carrega o `transacoes_treino.csv` e o Python lê os arquivos JSON de configuração.
2.  **Processamento Python (Hard Logic):** Antes de chamar a IA, scripts Python calculam os totais, identificam duplicidades e filtram a lista de produtos permitidos baseados no perfil do usuário logado.
3.  **Montagem:** Apenas os dados processados e relevantes são passados para o contexto.

### Como os dados são usados no prompt?
Utilizamos a técnica de **Context Injection** dinâmica dentro do *System Prompt*. Os dados não são estáticos; eles mudam conforme o estado do usuário.

* **Perfil:** As regras do JSON (`regras_agente`) são injetadas como diretrizes de comportamento ("Seja rígido" ou "Seja motivador").
* **Transações:** O CSV não é enviado inteiro se for grande. Enviamos um resumo sumarizado (Top 5 gastos, Total Fixo vs Variável) e as anomalias detectadas pelo Python.
* **Produtos:** Apenas se o usuário demonstrar intenção de investimento, o JSON filtrado é anexado ao prompt.

---

## Exemplo de Contexto Montado

> Mostre um exemplo de como os dados são formatados para o agente.

## Exemplo de Contexto Montado

Abaixo, um exemplo de como o prompt final chega ao Gemini para um usuário do tipo **Equilibrista**:

```text
--- INSTRUÇÃO DO SISTEMA ---
Você é o Sentinela, um assistente financeiro.
TOM DE VOZ: Prático e Cauteloso (Alerta de risco).
REGRA CRÍTICA: Bloquear sugestões de parcelamentos novos.

--- DADOS DO USUÁRIO (Contexto Injetado) ---
Nome: Bruno
Status Atual: Alerta Amarelo (Saldo Livre Real: R$ 150,00)
Dias até o salário: 12

--- RESUMO FINANCEIRO (Processado do CSV) ---
- Total Gasto Mês: R$ 2.450,00
- Recorrências Fixas já pagas: Aluguel, Internet.
- ANOMALIA DETECTADA: Transação duplicada 'Apple Services' dia 10/10 (R$ 10,90).
- ALERTA: A conta 'Netflix' veio 40% acima da média histórica.

--- PERGUNTA DO USUÁRIO ---
"Posso assinar um clube de vinhos de 80 reais?"
```
