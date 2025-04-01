# RAG com FastAPI

## Descrição
Este projeto implementa um sistema de Retrieval-Augmented Generation (RAG) utilizando **FastAPI** e **SentenceTransformers** para gerar respostas baseadas em documentos pré-definidos. A API realiza a busca no conteúdo mais relevante e gera respostas com o modelo **Groq**.

**⚠ Aviso: Este projeto está em estado inicial e pode conter funcionalidades incompletas ou instáveis.**

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