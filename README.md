# dns-log-generator

Simulador estocástico e determinístico em Python para geração de tráfego DNS benigno realista no formato nativo de `query logging` do **ISC BIND 9**.

Desenvolvido no âmbito do Trabalho de Conclusão de Curso (DCC/UFRR) *"Detecção de Ataques NXDOMAIN Flood em Servidores DNS Utilizando Isolation Forest"* para produzir a linha de base de **48 horas contínuas** (89,17 milhões de consultas brutas de 25.000 clientes), podendo ser utilizado de forma independente em pesquisas e testes de carga em servidores DNS.

---

## Ecossistema do Experimento

Se você deseja apenas **reproduzir o experimento e os gráficos do TCC sem gerar ~12 GB de logs do zero**, o dataset pronto já está publicado no Kaggle:

| Componente | Onde encontrar | Uso recomendado |
| :--- | :--- | :--- |
| **Dataset Completo (Kaggle)** | [kaioguilherme/dns-nxdomain-flood-benign-48h](https://www.kaggle.com/datasets/kaioguilherme/dns-nxdomain-flood-benign-48h) · DOI [`10.34740/KAGGLE/DSV/22300671`](https://doi.org/10.34740/KAGGLE/DSV/22300671) | Baixar diretamente `benigno_unificado.log` (11,94 GB), `ataques_unificados.log` ou `dns_eventos_estruturados_48h.csv.gz`. |
| **Pipeline de Detecção e Gráficos** | [Kaioguilherme1/nxdomain-flood-iforest-tcc](https://github.com/Kaioguilherme1/nxdomain-flood-iforest-tcc) | Treinar o *Isolation Forest*, rodar a comparação com *Nadler et al. (2019)* e gerar as figuras/tabelas do TCC. |
| **Este Repositório (`dns-log-generator`)** | Código-fonte atual | Reproduzir ou customizar do zero a geração estocástica de tráfego DNS benigno em formato BIND 9. |

---

## Principais Características

* **Determinismo Científico:** Controlado por semente única (`SEED = 129547711` em `config/config.py`), garantindo a mesma sequência de clientes, IPs, portas e consultas em qualquer execução.
* **População e Perfis Comportamentais:** Emula `25.000` clientes na sub-rede `10.0.0.0/16` distribuídos em 5 perfis (`config/profiles.yaml`: `student_user` 25%, `office_employee` 25%, `home_user` 25%, `casual_mobile_user` 20% e `devops_engineer` 5%), reproduzindo ciclo circadiano (madrugada, transição e horário comercial).
* **Distribuição Realista de Domínios e Consultas:** Utiliza rankings consolidados do **Cloudflare Radar** (`datasets/`) com seleção ponderada aproximando a **Lei de Zipf** e proporções empíricas de tipos de registro (`A` 64,0%, `AAAA` 21,0%, `MX` 3,1%, `CNAME` 2,7%, `NS` 2,0%, `PTR` 2,0%, `TXT` 1,1%).
* **Ruído Operacional Configurável:** Emula eventos benignos imperfeitos típicos de produção (`2%` de *timeouts*, `1%` de detecção de *loop*, `1%` de *cache denied* e `nxdomain_probability` por perfil).
* **Formato Nativo ISC BIND 9:** Registra linhas compatíveis diretamente com *parsers* padrão de `query logs` (`DD-Mon-YYYY HH:MM:SS.mmm client @0x... IP#PORT (DOMAIN): query: DOMAIN IN QTYPE +E(0) (192.168.0.10)`).

---

## Estrutura do Repositório

```text
dns-log-generator/
├── config/
│   ├── config.py            # Parâmetros globais (TOTAL_USERS, SIMULATION_HOURS, SEED)
│   ├── domain_list.json     # Lista ponderada de domínios e subdomínios
│   └── profiles.yaml        # Perfis comportamentais, janelas ativas e probabilidades
├── core/
│   ├── log_formatter.py     # Formatação exata de linhas de log ISC BIND 9
│   ├── logger.py            # Gerenciador de logs e rotação
│   ├── test_user.py         # Script de validação rápida de usuário e determinismo
│   ├── user.py              # Máquina de eventos de cada cliente simulado
│   ├── user_manager.py      # Instanciação determinística da população de clientes
│   └── utils.py             # Utilitários probabilísticos (seleção ponderada)
├── datasets/                # Amostras CSV do Cloudflare Radar + script de normalização
├── test/
│   └── test_generator.py    # Suíte de testes automatizados (pytest)
├── logs/                    # Diretório de saída dos logs gerados (dns_events.log)
├── main.py                  # Ponto de entrada da simulação (fila de prioridade / heap)
└── requirements.txt         # Dependências Python (PyYAML e pytest)
```

---

## Como Executar

### 1. Clonar e instalar dependências
```bash
git clone https://github.com/Kaioguilherme1/dns-log-generator.git
cd dns-log-generator

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Validar instalação e determinismo (testes rápidos)
```bash
pytest -v
python3 core/test_user.py
```

### 3. Gerar os logs DNS
* **Teste rápido (opcional):** Antes de rodar a simulação completa de 48h (~11,94 GB / ~89M de linhas), você pode editar temporariamente `TOTAL_USERS` (ex.: `100`) e `SIMULATION_HOURS` (ex.: `1`) em `config/config.py`.
* **Execução oficial completa (`TOTAL_USERS = 25000`, `SIMULATION_HOURS = 48`, `SEED = 129547711`):**
```bash
python3 main.py
```
Os registros serão gravados em `logs/dns_events.log` (com registro operacional em `logs/system.log`).

---

## Integração com o Pipeline do TCC

Se você acabou de baixar o dataset pronto no [Kaggle (`dns-nxdomain-flood-benign-48h`)](https://www.kaggle.com/datasets/kaioguilherme/dns-nxdomain-flood-benign-48h) (DOI [`10.34740/KAGGLE/DSV/22300671`](https://doi.org/10.34740/KAGGLE/DSV/22300671)) ou gerou `logs/dns_events.log` com este simulador, utilize o repositório **[nxdomain-flood-iforest-tcc](https://github.com/Kaioguilherme1/nxdomain-flood-iforest-tcc)** para realizar a preparação dos dados, extração de atributos em janelas de 30 s, treinamento do *Isolation Forest* e geração automática de todas as figuras e tabelas do TCC.

---

## Como Citar o Dataset

```bibtex
@misc{kaio_guilherme_ferraz_de_sousa_silva_2026,
  title     = {DNS NXDOMAIN Flood & Benign Traffic Dataset (48h)},
  url       = {https://www.kaggle.com/dsv/22300671},
  doi       = {10.34740/KAGGLE/DSV/22300671},
  publisher = {Kaggle},
  author    = {Kaio Guilherme Ferraz de Sousa Silva},
  year      = {2026}
}
```
