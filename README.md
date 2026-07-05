# Cable

O **Cable** é um aplicativo desktop simples construído para ajudar estudantes de **Ciência da Computação do CEFET/RJ** a gerenciarem suas horas de Atividades Complementares de acordo com as regras estabelecidas pelo regulamento interno do DEPIN.

O sistema calcula automaticamente o teto máximo aceito por tipo de atividade, exibe gráficos interativos de rosca sobre seu progresso e notifica quando você atinge as **230 horas obrigatórias** necessárias,

---

## ✨ Funcionalidades
- Soma de horas baseando-se nos tetos máximos individuais de cada categoria (Pesquisa, Extensão, Ensino e Conscientização).
- Gráficos interativos renderizados em tempo real e barra de progresso visual (barra ainda em progresso).
- Clique nos cards de resumo ou use a barra lateral para ver e gerenciar registros de cada tipo de atividade.
- Adicione, edite e remova registros detalhados informando nome, categoria, subcategoria, horas, data e links/observações de certificados.
- Salva tudo automaticamente em um arquivo `data.json` na mesma pasta do app. Então não perca esse arquivo!

---

## Como Rodar o Projeto Localmente

### Pré-requisitos
Ter o **Python 3.8 ou superior** instalado.

### Passo 1: Clonar o Repositório
Abra o seu terminal ou prompt de comando e clone o projeto:
```bash
git clone [https://github.com/SEU-USUARIO/cable.git](https://github.com/SEU-USUARIO/cable.git)
cd cable
```

### Passo 2: Instalar as Dependências
Instale as bibliotecas necessárias utilizando o pip:
```bash
pip install -r requirements.txt
```

### Passo 3: Executar a Aplicação
Inicie o aplicativo executando o comando:
```bash
python main.py
```