def retrive_docs(vector_store, query):
    Retrival = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3},
    )
    docs = Retrival.invoke(query)
    return docs


def Rerank_docs(query, vector_store):
    docs = retrive_docs(vector_store, query)
    Reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L12-v2")
    pairs = [(query, d.page_content) for d in docs]
    scores = Reranker.predict(pairs)
    ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
    return [doc for doc, _ in ranked]


def Build_response(query, vector_store):
    top_docs = Rerank_docs(query, vector_store)
    context = "\n\n".join(d.page_content for d in top_docs)
    rag_chain = template | model
    response = rag_chain.invoke({
        "context": context,
        "question": query,
    })
    return response.content