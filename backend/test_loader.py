from app.rag.loader import load_pdf
from app.rag.splitter import split_documents

docs = load_pdf("data/uploads/resumes/f67bbf92-75a9-4a1b-83a9-de3e90296f18_final_sneha_pankhi_.pdf")

chunks = split_documents(docs)

print(len(chunks))

print(chunks[0].page_content)