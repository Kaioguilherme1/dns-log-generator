# Modelo  de Perfil de Usuário para Simulação DNS

## 1. Objetivo

Este documento descreve o funcionamento do modelo simplificado de perfil de usuário utilizado para simulação de tráfego DNS.

O modelo controla:

* Quando o usuário gera tráfego
* Com qual intensidade
* Com quais domínios base
* Com quais características comportamentais
* Como o tráfego é rotulado

---

# 2. Estrutura Geral do Perfil

```yaml
profile:
  id:
  name:
  category:

  usability_window:
    start:
    end:
    timezone:

  traffic_profile:
    base_requests_per_minute:
    burst_probability:
    burst_multiplier:

  domain_base:
    list_name:

  behavior_controls:
    subdomain_probability:
    nxdomain_probability:
    reuse_domain_probability:

  labeling:
    default_flag:
    tag:
```

---

# 3. Descrição de Cada Campo

---

# 3.1 Bloco `profile`

## `id`

Identificador numérico único do perfil.
Utilizado para rastreabilidade experimental e controle de versões.

## `name`

Nome descritivo do perfil.
Usado para identificação lógica e documentação.

## `category`

Classificação comportamental do perfil.

Valores típicos:

* `normal`
* `infraestrutura`
* `anomalo`

---

# 3.2 Bloco `usability_window`

Define o intervalo diário no qual o perfil pode gerar tráfego.

## `start`

Horário inicial da atividade (formato HH:MM).

## `end`

Horário final da atividade (formato HH:MM).

## `timezone`

Fuso horário aplicado ao perfil.
Garante consistência temporal nos experimentos.

Fora dessa janela, o perfil não gera consultas.

---

# 3.3 Bloco `traffic_profile`

Controla intensidade e padrão de geração de requisições.

## `base_requests_per_minute`

Quantidade média de requisições por minuto em condição normal.

Representa o fluxo contínuo típico do usuário.

---

## `burst_probability`

Probabilidade de ocorrer uma rajada de requisições em determinado minuto.

Simula:

* Abertura de múltiplas abas
* Carregamento de páginas complexas
* Atualizações simultâneas

Valor entre 0 e 1.

---

## `burst_multiplier`

Fator multiplicador aplicado à taxa base quando ocorre burst.

Exemplo:

* Base = 20 req/min
* Multiplier = 3
* Durante burst = 60 req/min

---

# 3.4 Bloco `domain_base`

Define qual conjunto de domínios o perfil utilizará.

## `list_name`

Nome lógico da lista de domínios definida externamente.

Exemplos:

* `web_services`
* `mail_providers`
* `cloud_infrastructure`
* `malicious_c2`

Observação:
A distribuição de QTYPE não é definida aqui.
Ela pertence ao modelo de domínio.

---

# 3.5 Bloco `behavior_controls`

Controla variabilidade comportamental.

---

## `subdomain_probability`

Probabilidade de gerar um subdomínio aleatório.

Exemplo:

```
abcd1234.google.com
```

Valores altos indicam:

* Maior variabilidade
* Possível comportamento automatizado

---

## `nxdomain_probability`

Probabilidade de gerar uma consulta inválida (domínio inexistente).

Utilizado para simular:

* Erro humano
* DGA
* Comportamento malicioso

---

## `reuse_domain_probability`

Probabilidade de repetir um domínio recentemente consultado.

Simula:

* Cache DNS
* Navegação natural
* Padrão humano de acesso repetido

---

# 3.6 Bloco `labeling`

Define rotulagem supervisionada para datasets.

---

## `default_flag`

Valor numérico associado ao perfil.

Exemplo:

* 0 → benigno
* 1 → malicioso

---

## `tag`

Rótulo textual do perfil.

Exemplos:

* benign
* malicious
* infrastructure

---

# 4. Modelo Comportamental Representado

Este perfil controla:

* Intensidade temporal
* Padrão de rajada
* Seleção de grupo de domínios
* Variabilidade estrutural do nome consultado
* Probabilidade de erro
* Rotulagem para aprendizado supervisionado






