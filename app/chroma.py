from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_text_splitters import CharacterTextSplitter


def insert_document(
    file_path: str,
    id: str,
    persistent_client: Chroma,
):
    langchain_chroma = Chroma(
        client=persistent_client,
        collection_name="collection_name",
        embedding_function=embedding_function,
    )

    # load the document and split it into chunks
    loader = TextLoader(file_path)
    documents = loader.load()

    # split it into chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)

    # create the open-source embedding function
    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    persistent_client.add_documents(docs, embedding_function)


# load it into Chroma
db = Chroma.from_documents(docs, embedding_function)

# query it
query = "What did the president say about Ketanji Brown Jackson"
docs = db.similarity_search(query)

# print results
print(docs[0].page_content)
