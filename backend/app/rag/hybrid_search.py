from backend.app.rag.rrf import reciprocal_rank_fusion


def hybrid_search(query, bm25_retriever, vector_retriever):

    bm25_docs = bm25_retriever.invoke(query)

    vector_docs = vector_retriever.invoke(query)

    return reciprocal_rank_fusion(
        [bm25_docs, vector_docs]
    )