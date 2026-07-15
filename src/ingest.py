"""
Ingestão do corpus de políticas de RH para o ChromaDB.

Divide o markdown de políticas em chunks por política (POL-XXX) e gera
embeddings usando Google Gemini (free tier). Cada chunk mantém metadados
de rastreabilidade: id da política, versão e vigência — pensado para
auditoria, no mesmo espírito de rastreabilidade requisito-evidência usado
em ambientes regulados.
"""

import os
import re
from pathlib import Path

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

DATA_PATH = Path(__file__).parent.parent / "data" / "politicas_rh.md"
PERSIST_DIR = Path(__file__).parent.parent / "chroma_db"

POLICY_PATTERN = re.compile(
    r"## (POL-\d+) — (.+?)\n\n\*\*Vigência:\*\* (.+?)\n\*\*Versão:\*\* (.+?)\n\n(.*?)(?=\n---|\Z)",
    re.DOTALL,
)


def parse_policies(raw_text: str) -> list[Document]:
    """Extrai cada política como um Document com metadados estruturados."""
    documents = []
    for match in POLICY_PATTERN.finditer(raw_text):
        policy_id, title, vigencia, versao, body = match.groups()
        documents.append(
            Document(
                page_content=f"{title}\n\n{body.strip()}",
                metadata={
                    "policy_id": policy_id,
                    "title": title.strip(),
                    "vigencia": vigencia.strip(),
                    "versao": versao.strip(),
                },
            )
        )
    return documents


def build_index() -> None:
    raw_text = DATA_PATH.read_text(encoding="utf-8")
    documents = parse_policies(raw_text)

    print(f"[ingest] {len(documents)} políticas extraídas do corpus.")

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=os.environ["GOOGLE_API_KEY"],
    )

    Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=str(PERSIST_DIR),
        collection_name="politicas_rh",
    )

    print(f"[ingest] Índice persistido em {PERSIST_DIR}")


if __name__ == "__main__":
    build_index()
