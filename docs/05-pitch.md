# Pitch: Sentinela - Seu Guardião Financeiro

> [!TIP]
> Use este roteiro como base para gravar seu vídeo de 3 minutos. Fale com naturalidade e entusiasmo!
 
## Roteiro do Pitch

### 1. O Problema (30 seg)
> **"Por que as pessoas falham em organizar as finanças?"**

A maioria dos apps financeiros são apenas "planilhas de luxo": eles mostram o gráfico do passado, mas não dizem o que fazer no futuro.
Além disso, o conselho financeiro genérico falha. Dizer "invista em ações" para quem está endividado é irresponsável. Dizer "corte o cafezinho" para quem já tem as contas em dia é irritante.
As pessoas precisam de um **contexto** que entenda se elas precisam de "amor duro" para sair das dívidas ou de "estratégia" para multiplicar capital.

### 2. A Solução (1 min)
> **"Apresentando o Sentinela: Inteligência com Contexto"**

O Sentinela não é apenas um chatbot. Ele é um **Agente Financeiro Ativo** que combina a potência do Google Gemini com uma arquitetura de dados robusta e segura.

Nossos 3 pilares são:
1.  **Hiper-Personalização:** O sistema carrega perfis comportamentais (JSON) que alteram a "personalidade" da IA. Ele é rígido com o endividado e motivador com o investidor.
2.  **Memória Persistente:** Diferente de chats comuns que esquecem tudo ao fechar a aba, o Sentinela usa um banco de dados SQLite para lembrar do histórico do usuário, Renda e Despesas Fixas, criando uma conversa contínua.
3.  **Segurança e Privacidade:** Implementamos "Guardrails" que impedem a IA de alucinar produtos inexistentes e garantem isolamento total dos dados entre usuários.

### 3. Demonstração (1 min)
> **"Vamos ver na prática" (Sugestão de fluxo para o vídeo)**

1.  **Tela de Login:** Mostre o cadastro de um novo usuário (ex: "Maria") informando Renda e Despesas Fixas. Destaque que o sistema cria um ID único no Banco de Dados.
2.  **Onboarding:** Mostre o Agente dando as boas-vindas personalizadas, já calculando quanto sobra do salário.
3.  **Interação:** Faça uma pergunta como "Posso gastar 500 reais em um jantar?". Mostre o agente negando (se for perfil endividado) ou ponderando (se for perfil investidor).
4.  **Ferramenta:** Peça "Gere um relatório" e mostre o botão de download CSV aparecendo automaticamente.

### 4. Diferencial e Impacto (30 seg)
> **"O que nos torna únicos?"**

Enquanto o mercado oferece dashboards estáticos, nós oferecemos **Consultoria Escalonável**.
Nosso diferencial técnico é a arquitetura híbrida: usamos LLM para a interpretação natural, mas **código Python rígido (Pandas/SQL)** para os cálculos matemáticos. Isso elimina o risco da IA "inventar" números.
O impacto é a democratização do planejador financeiro pessoal, acessível 24/7 e adaptado à realidade de cada brasileiro.

---

## Checklist do Pitch

- [x] Duração máxima de 3 minutos
- [x] Problema: Falta de personalização e memória em apps atuais.
- [x] Solução: Agente com Banco de Dados e Perfis Comportamentais.
- [x] Demonstração: Fluxo de Login -> Chat -> Download CSV.
- [x] Diferencial: Memória persistente e cálculos via Python (Anti-alucinação).