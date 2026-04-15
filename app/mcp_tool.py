from mcp.server.fastmcp import FastMCP
from typing import Optional
from chatbot import ask

# ── Server init ───────────────────────────────────────────────────────────────

mcp = FastMCP(
    name="banks-banjo-glean",
    instructions=(
        "This tool answers questions about Banks & Banjo LLC internal HR "
        "policies. It retrieves information from indexed HR documents covering "
        "onboarding, PTO, benefits, org structure, and performance reviews."
    ),
)

# ── Tool definition ───────────────────────────────────────────────────────────

@mcp.tool()
def glean_chat(
    question: str,
    datasource: Optional[str] = None,
    top_k: Optional[int] = 5,
    include_citations: Optional[bool] = True,
) -> dict:
           
    if not question or not question.strip():
        raise ValueError("'question' is required and cannot be empty.")

    result = ask(
        question=question.strip(),
        top_k=top_k or 5,
        datasource=datasource or None,
        include_citations=include_citations if include_citations is not None else True,
    )

    return result


# ── Entrypoint ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # stdio transport: the MCP client (Cursor, Claude Desktop, etc.) launches
    # this script as a subprocess and communicates over stdin/stdout.
    # Do NOT print anything to stdout in this file — it will corrupt the
    # MCP protocol stream. Use stderr for any debug output if needed.
    mcp.run(transport="stdio")
