import pandas as pd
import os
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
import faiss
import yaml
from langchain_community.vectorstores import FAISS
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate

with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)
os.environ['GOOGLE_API_KEY'] = config['google_api_key']
API_KEY = os.environ['GOOGLE_API_KEY']

# df = pd.DataFrame({
#             "id" : [1, 2],
#             "titulo" : ["Imagem1", "Imagem2"],
#             "valor" : [0.7, 0.15],
#             "descricao" : ["a coluna valor representa a quantidade de verde na imagem1",
#                            "a coluna valor representa a quantidade de verde na imagem 2"]})


def df_to_langchain_documents(df: pd.DataFrame, content_columns: list) -> list[Document]:
    """Converte linhas do DataFrame em Documentos LangChain."""
    documents = []
    for _, row in df.iterrows():
        content = " | ".join([f"{col}: {row[col]}" for col in content_columns])
        doc = Document(
            page_content=content,
            metadata={"source": "pandas_dataframe", "id": row['id']}
        )
        documents.append(doc)
    return documents

# content_cols = ['titulo', 'descricao', 'valor']

# langchain_documents = df_to_langchain_documents(df, content_cols)


def modelo(langchain_documents):
# 🧠 1. SUBSTITUIÇÃO DO MODELO DE EMBEDDINGS
# Usando o modelo de embedding do Gemini

    embeddings = GoogleGenerativeAIEmbeddings(model="text-embedding-004")

# Crie o Vector Store com os documentos
    vectorstore = FAISS.from_documents(
        documents=langchain_documents,
        embedding=embeddings
    )

# Crie o Retriever para buscar documentos relevantes
    retriever = vectorstore.as_retriever()

# 🤖 2. SUBSTITUIÇÃO DO MODELO DE CHAT
# Usando o modelo Gemini mais adequado para chat/instrução
# gemini-2.5-flash é rápido e eficiente para tarefas de resumo.
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# O Prompt e a estrutura da cadeia RAG (LCEL) permanecem os mesmos
    prompt = ChatPromptTemplate.from_template("""
    Você é um assistente de resumo. Sua tarefa é criar um resumo conciso e informativo 
    dos seguintes dados, focando em **comparação da quantidade de area vere em cada imagem**.

    Dados do Contexto:
    {context}

    Resumo solicitado:
    {input}
    """)

# 1. Cadeia de Combinação de Documentos (Stuffing)
    document_chain = create_stuff_documents_chain(llm, prompt)

    # 2. Cadeia de Busca (Retrieval)
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    # 🎯 A Pergunta ou Comando para o Resumo
    query = "Crie um resumo explicando as principais diferencas entre cada area verde."

    # 🏃 Execute a Cadeia RAG
    response = retrieval_chain.invoke({"input": query})

## 📝 Resultado do Resumo

    print("---")
    print(f"**Pergunta de Busca (Query):** {query}")
    print("---")
    print(f"**Resumo Gerado (Resposta):**\n{response['answer']}")
    print("---")
    print(f"**Documentos Usados (Contexto):**")
    for doc in response['context']:
        print(f"- {doc.metadata['id']}: {doc.page_content[:50]}...")

    return response  