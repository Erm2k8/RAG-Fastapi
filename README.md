# RAG com FastAPI

## Descrição
Este projeto implementa um sistema de Retrieval-Augmented Generation (RAG) utilizando **FastAPI** e **SentenceTransformers** para gerar respostas baseadas em documentos pré-definidos. A API realiza a busca no conteúdo mais relevante e gera respostas com o modelo **Groq**.

**⚠ Aviso: Este projeto está em estado inicial e pode conter funcionalidades incompletas ou instáveis.**

## Setup Inicial

1. Clone o repositório e instale as dependências:
    ```bash
    git clone https://github.com/Erm2k8/rag-fastapi.git
    cd rag-fastapi
    pip install -r requirements.txt
    ```

2. Crie o arquivo `.env` com a chave da API:
    ```bash
    GROQ_API_KEY=your_api_key
    ```

3. Execute o servidor:
    ```bash
    uvicorn main:app --reload
    ```
