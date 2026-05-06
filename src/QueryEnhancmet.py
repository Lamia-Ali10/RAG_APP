from langchain_core.prompts import ChatPromptTemplate,PromptTemplate
def query_rewrite(query):
  template = PromptTemplate(
      input_variables=["query"],
      template=(
          "You are an expert in information retrieval.\n"
          "Rewrite the following user query to be more specific, detailed, "
          "and aligned with terminology likely used in technical and regulatory documents.\n"
          "Do NOT answer the query.\n"
          "Return ONLY the rewritten query.\n\n"
          "Original query: {query}"
          )
  )
  chain = template|model
  return chain.invoke({"query":query})
