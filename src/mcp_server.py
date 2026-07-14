"""
Servidor MCP — HR Policy Agent

Expõe o motor de consulta de políticas de RH (query_engine.py) como tools
via Model Context Protocol, para que qualquer host compatível com MCP
(Claude Desktop, outro agente, etc.) possa consultá-lo.

Rodar localmente:
    python src/mcp_server.py

Configuração de exemplo para um host MCP (ex: Claude Desktop):
    {
      "mcpServers": {
        "hr-policy-agent": {
          "command": "python",
          "args": ["/caminho/absoluto/para/src/mcp_server.py"],
          "env": {"GOOGLE_API_KEY": "sua-chave-aqui"}
        }
      }
    }
"""

from mcp.server.fastmcp import FastMCP

from query_engine import PolicyQueryEngine

mcp = FastMCP("hr-policy-agent")
engine = PolicyQueryEngine()


@mcp.tool()
def consultar_politica(tema: str) -> dict:
    """
    Consulta a política de RH vigente sobre um tema (ex: 'férias',
    'licença maternidade', 'home office'). Retorna a resposta e os IDs
    das políticas usadas como fonte.
    """
    return engine.consultar_politica(tema)


@mcp.tool()
def verificar_elegibilidade(funcionario_contexto: str, beneficio: str) -> dict:
    """
    Verifica se um colaborador é elegível a um benefício específico.

    Args:
        funcionario_contexto: descrição do perfil do colaborador
            (ex: "CLT, banda 3, tempo integral" ou "PJ, sem cláusula específica").
        beneficio: nome do benefício a verificar (ex: "vale-refeição",
            "licença paternidade estendida").
    """
    return engine.verificar_elegibilidade(funcionario_contexto, beneficio)


@mcp.tool()
def resumir_mudancas(periodo_descricao: str = "versão mais recente") -> dict:
    """
    Resume as políticas vigentes e suas versões/vigências, simulando um
    changelog institucional (útil para auditoria e onboarding de RH).
    """
    return engine.resumir_mudancas(periodo_descricao)


if __name__ == "__main__":
    mcp.run(transport="stdio")
