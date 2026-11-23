def reciprocal_rank_fusion(results, k=60):
    """
    Fuse several ranked lists of LangChain Documents with Reciprocal
    Rank Fusion and return the Documents (de-duplicated by content),
    best first.
    """

    fused_scores = {}
    documents = {}

    for docs in results:
        for rank, doc in enumerate(docs, start=1):
            doc_id = doc.page_content

            documents.setdefault(doc_id, doc)

            fused_scores[doc_id] = (
                fused_scores.get(doc_id, 0) + 1 / (k + rank)
            )

    ranked_ids = sorted(
        fused_scores,
        key=fused_scores.get,
        reverse=True
    )

    return [documents[doc_id] for doc_id in ranked_ids]
