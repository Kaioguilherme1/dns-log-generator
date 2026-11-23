# Como Funciona a Seleção Ponderada

## Estrutura do JSON

O arquivo `domain_list.json` contém duas listas: `domains` e `subdomains`. Cada item é uma lista com duas partes:
1. **Nome** (domínio ou subdomínio)
2. **Peso** (número decimal entre 0 e 1 com duas casas decimais, representando a probabilidade relativa)

```json
{
  "domains": [
    ["google.com", 0.25],
    ["github.com", 0.20],
    ["stackoverflow.com", 0.15]
  ],
  "subdomains": [
    ["www", 0.40],
    ["api", 0.20],
    ["cdn", 0.15]
  ]
}
```

## Como os Pesos Funcionam

O algoritmo usa **seleção ponderada aleatória** (weighted random selection) através do método `random.choices()` do Python.

### Cálculo de Probabilidade

Para cada lista, a probabilidade de um item ser selecionado é:

```
Probabilidade = Peso do Item / Soma Total dos Pesos
```

### Exemplo com Domínios

Considerando os domínios:
- google.com: peso 0.25
- github.com: peso 0.20
- stackoverflow.com: peso 0.15
- wikipedia.org: peso 0.15
- arxiv.org: peso 0.10
- youtube.com: peso 0.08
- facebook.com: peso 0.05
- twitter.com: peso 0.02

**Soma total = 1.00**

Probabilidades (quando somam 1.00, o peso = probabilidade):
- google.com: 0.25/1.00 = 25%
- github.com: 0.20/1.00 = 20%
- stackoverflow.com: 0.15/1.00 = 15%
- wikipedia.org: 0.15/1.00 = 15%
- arxiv.org: 0.10/1.00 = 10%
- youtube.com: 0.08/1.00 = 8%
- facebook.com: 0.05/1.00 = 5%
- twitter.com: 0.02/1.00 = 2%

### Exemplo com Subdomínios

Considerando os subdomínios:
- www: peso 0.40
- api: peso 0.20
- cdn: peso 0.15
- mail: peso 0.10
- docs: peso 0.08
- blog: peso 0.05
- dev: peso 0.02

**Soma total = 1.00**

Probabilidades (quando somam 1.00, o peso = probabilidade):
- www: 0.40/1.00 = 40%
- api: 0.20/1.00 = 20%
- cdn: 0.15/1.00 = 15%
- mail: 0.10/1.00 = 10%
- docs: 0.08/1.00 = 8%
- blog: 0.05/1.00 = 5%
- dev: 0.02/1.00 = 2%

## Importante

- Os pesos **não precisam** somar exatamente 1.00. Eles são proporcionais.
- Quando somam 1.00, o peso representa diretamente a probabilidade (0.25 = 25%)
- Exemplo: `[["google.com", 0.50], ["github.com", 0.30]]` (soma 0.80) tem o mesmo efeito proporcional
- Peso maior = maior probabilidade de ser escolhido
- Peso 0.00 = nunca será escolhido (não recomendado, melhor remover da lista)
- Recomenda-se usar valores entre 0.01 e 1.00 com duas casas decimais

## Como Editar

Para aumentar a frequência de um domínio/subdomínio:
```json
["google.com", 0.50]  // Aumenta de 0.25 para 0.50 - dobra a probabilidade relativa
```

Para diminuir:
```json
["twitter.com", 0.01]  // Diminui de 0.02 para 0.01 - reduz pela metade
```

Para adicionar novo item:
```json
{
  "domains": [
    ["google.com", 0.25],
    ["meusite.com", 0.10]  // Adiciona novo domínio com peso 0.10 (10%)
  ]
}
```

### Dicas de Configuração

**Para distribuição uniforme**, use o mesmo peso para todos:
```json
["google.com", 0.25], ["github.com", 0.25], ["stackoverflow.com", 0.25], ["wikipedia.org", 0.25]
```

**Para priorizar muito um item**, use peso alto:
```json
["google.com", 0.70], ["github.com", 0.15], ["stackoverflow.com", 0.10], ["wikipedia.org", 0.05]
```

**Para item raro**, use peso baixo:
```json
["dominio-raro.com", 0.01]  // Aparece apenas 1% das vezes (se total = 1.00)
```

## Implementação no Código

O código verifica automaticamente se os dados estão no formato ponderado:
- Se encontrar formato `[["nome", peso]]` → usa seleção ponderada
- Se encontrar formato `["nome1", "nome2"]` → usa seleção uniforme (todos têm mesma chance)

Isso permite usar o sistema com ou sem pesos conforme necessário.

