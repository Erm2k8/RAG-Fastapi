# RAG com FastAPI

## Descrição
Este projeto implementa um sistema de Retrieval-Augmented Generation (RAG) utilizando **FastAPI** e **SentenceTransformers** para gerar respostas baseadas em documentos pré-definidos. A API realiza a busca no conteúdo mais relevante e gera respostas com o modelo **Groq**.

## Recursos
- **Processamento de Documentos**: Ingestão de PDFs e extração de texto  
- **Armazenamento Vetorial**: ChromaDB para armazenamento eficiente de embeddings  
- **Busca Semântica**: SentenceTransformers para correspondência por relevância  
- **Integração com LLM**: API do Groq para geração de respostas  

## Estrutura do projeto

```text
rag-fastapi/
├── app/
│   ├── api/              # Rotas e esquemas da API
│   ├── core/             # Configurações e utilitários
│   ├── data/             # Armazenamento de dados
│   │   ├── documents/    # Armazenamento dos arquivos-fonte
│   │   └── vectors/      # Coleções do ChromaDB
│   ├── services/         # Módulos de processamento
│   └── main.py           # Ponto de entrada do FastAPI
├── .env                  # Variáveis de ambiente
├── requirements.txt      # Dependências do Python
└── README.md             # Documentação do projeto
```

## Principais Endpoints

| Endpoint | Método | Descrição                          |
|----------|--------|------------------------------------|
| `v1/upload/` | POST   | Processa e indexa documentos       |
| `v1/query/`  | POST   | Submete consultas RAG              |
| `v1/documents/`   | GET    | Lista os documentos armazenados     |

## Setup Inicial

1. Clone o repositório
    ```bash
    git clone https://github.com/Erm2k8/rag-fastapi.git
    cd rag-fastapi
    ```

2. Crie um ambiente virtual e instale as dependências
    ```bash
    python -m venv venv
    venv\Scripts\activate
    python -m pip install -r requirements.txt
    ```

3. Crie o arquivo `.env` com a chave da API:
    ```bash
    GROQ_API_KEY=your_api_key
    ```

4. Execute o servidor:
    ```bash
    cd app
    uvicorn main:app --reload
    ```

5. Acesse o endpoint de documentação para testar a API:
    ```bash
    http://localhost:8000/docs
    ```