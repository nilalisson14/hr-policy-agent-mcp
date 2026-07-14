"""
Teste manual do engine de consulta (sem MCP), para validar o RAG
isoladamente antes de expor via protocolo.

Rodar:
    python tests/test_query_engine_manual.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from query_engine import PolicyQueryEngine  # noqa: E402


def main() -> None:
    engine = PolicyQueryEngine()

    print("=== Teste 1: consultar_politica ===")
    resultado = engine.consultar_politica("posso fracionar minhas férias?")
    print(resultado["resposta"])
    print("Fontes:", resultado["fontes"])

    print("\n=== Teste 2: verificar_elegibilidade ===")
    resultado = engine.verificar_elegibilidade(
        funcionario_contexto="PJ, tempo integral", beneficio="vale-refeição"
    )
    print(resultado["resposta"])
    print("Fontes:", resultado["fontes"])

    print("\n=== Teste 3: resumir_mudancas ===")
    resultado = engine.resumir_mudancas("afastamento e saúde")
    for pol in resultado["politicas"]:
        print(pol)


if __name__ == "__main__":
    main()
