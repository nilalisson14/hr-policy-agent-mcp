"""
Motor de consulta sobre o índice de políticas de RH.

Isolado do servidor MCP de propósito: as tools do MCP só orquestram
chamadas para cá, o que facilita testar o RAG isoladamente (inclusive
com RAGAS) sem precisar subir o protocolo MCP.
"""

import os
from pathlib import Path

from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma

PERSIST_DIR = Path(__file__).parent.parent / "chroma_db"

_SYSTEM_PROMPT = """Você é um assistente de políticas de RH. Responda SOMENTE
com base nos trechos de política fornecidos abaixo. Se a informação não
estiver nos trechos, diga explicitamente que não encontrou a política e
não invente uma resposta.

Sempre cite o ID da política (ex: POL-001) usada como base da resposta.

Trechos de política:
{context}

Pergunta: {question}
"""


class PolicyQueryEngine:
    def __init__(self) -> None:
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=os.environ["GOOGLE_API_KEY"],
        )
        self.vectorstore = Chroma(
            persist_directory=str(PERSIST_DIR),
            embedding_function=embeddings,
            collection_name="politicas_rh",
        )
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=os.environ["GOOGLE_API_KEY"],
            temperature=0,
        )

    def _retrieve(self, query: str, k: int = 3):
        return self.vectorstore.similarity_search(query, k=k)

    def consultar_politica(self, tema: str) -> dict:
        """Busca e responde sobre um tema de política de RH (ex: 'férias')."""
        docs = self._retrieve(tema)
        context = "\n\n".join(
            f"[{d.metadata['policy_id']}] {d.page_content}" for d in docs
        )
        prompt = _SYSTEM_PROMPT.format(context=context, question=tema)
        response = self.llm.invoke(prompt)
        return {
            "resposta": response.content,
            "fontes": [d.metadata["policy_id"] for d in docs],
        }

    def verificar_elegibilidade(self, funcionario_contexto: str, beneficio: str) -> dict:
        """
        Verifica elegibilidade a um benefício dado um contexto descritivo
        do funcionário (ex: 'PJ, tempo integral' ou 'CLT, banda 3').
        """
        query = f"elegibilidade {beneficio} para {funcionario_contexto}"
        docs = self._retrieve(query)
        context = "\n\n".join(
            f"[{d.metadata['policy_id']}] {d.page_content}" for d in docs
        )
        prompt = _SYSTEM_PROMPT.format(
            context=context,
            question=(
                f"O colaborador com o seguinte perfil é elegível ao benefício "
                f"'{beneficio}'? Perfil: {funcionario_contexto}. "
                f"Responda SIM, NÃO, ou PARCIAL, com justificativa citando a política."
            ),
        )
        response = self.llm.invoke(prompt)
        return {
            "resposta": response.content,
            "fontes": [d.metadata["policy_id"] for d in docs],
        }

    def resumir_mudancas(self, periodo_descricao: str = "versão mais recente") -> dict:
        """
        Resume o que existe de política vigente relacionado ao período/versão
        informado. No corpus sintético isso reflete metadados de versão,
        simulando um changelog institucional.
        """
        docs = self.vectorstore.similarity_search(periodo_descricao, k=6)
        resumo = [
            {
                "policy_id": d.metadata["policy_id"],
                "titulo": d.metadata["title"],
                "versao": d.metadata["versao"],
                "vigencia": d.metadata["vigencia"],
            }
            for d in docs
        ]
        return {"politicas": resumo}
