# Aprendizagem de Gramática Artificial (AGL) - Experimento

Este programa implementa um experimento clássico de Aprendizagem de Gramática Artificial (AGL) usando PyGame. O experimento visa investigar a aquisição implícita de regularidades estruturais.

## Sobre o Experimento

O programa implementa as duas fases clássicas do paradigma AGL:

1. **Fase de Treinamento**: Os participantes veem sequências de letras geradas a partir de uma gramática de estado finito e são instruídos a memorizá-las.

2. **Fase de Teste**: Os participantes julgam novas sequências como "gramaticais" ou "não gramaticais" e indicam seu nível de confiança na decisão.

## Características do Programa

- **Gramática de Estado Finito**: Implementa uma gramática baseada no modelo Reber, mas com símbolos diferentes.
- **Interface Gráfica**: Interface intuitiva construída com PyGame.
- **Análise de Resultados**: Calcula métricas baseadas na teoria da detecção de sinais (índice d').
- **Salva Resultados**: Gera arquivos de texto (.txt) e CSV com todos os resultados e detalhes do experimento.

## Requisitos

- Python 3.6 ou superior
- PyGame

## Instalação

1. Certifique-se de ter Python instalado
2. Instale PyGame:

```
pip install pygame
```

## Como Executar

Execute o arquivo principal:

```
python agl_experiment.py
```

## Detalhes da Implementação

- O programa gera sequências gramaticais baseadas em regras de transição de estados.
- Sequências não gramaticais são geradas modificando sequências gramaticais.
- Durante o teste, são apresentadas 20 sequências (10 gramaticais, 10 não gramaticais).
- As métricas calculadas incluem: acurácia, d', hits, misses, falsos alarmes, rejeições corretas, confiança média e tempo de resposta médio.

## Resultados

Os resultados são salvos automaticamente em arquivos de texto (.txt) e CSV no diretório "resultados":

**Arquivo de texto (.txt):**
- Data e hora do experimento
- Métricas de desempenho (d', acurácia, etc.)
- Lista de sequências de treino
- Lista de sequências de teste e as respostas do participante

**Arquivo CSV:**
- Seção de métricas gerais (hits, misses, d', acurácia, etc.)
- Lista de sequências de treino
- Tabela de resultados do teste com colunas para sequência, classificação real, resposta do participante, nível de confiança e tempo de reação
#   t a r e f a 2  
 