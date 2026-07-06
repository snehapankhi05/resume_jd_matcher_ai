def reciprocal_rank_fusion(results, k=60):
    fused_scores = {}

    for docs in results:
        for rank, doc in enumerate(docs):
            doc_id = doc.page_content

            if doc_id not in fused_scores:
                fused_scores[doc_id] = 0

            fused_scores[doc_id] += 1 / (rank + k)

    reranked = sorted(
        fused_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return [doc for doc, _ in reranked]