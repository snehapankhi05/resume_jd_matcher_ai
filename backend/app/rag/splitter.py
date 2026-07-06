from langchain_text_splitters import RecursiveCharacterTextSplitter


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150,
    separators=[
        "\n\n",
        "\n",
        ". ",
        " ",
        ""
    ]
)


def split_documents(documents):
    """
    Split LangChain documents into smaller chunks.
    """

    chunks = text_splitter.split_documents(documents)

    return chunks