# """chains.py — show Responder vs Reviser flow with Rich panels
#
# Run the script and you’ll see in order:
# 1. **User Question**
# 2. **Responder**
#    • raw tool‑call ➜ parsed answer ➜ reflection ➜ search queries
# 3. **Reviser**
#    • raw tool‑call ➜ final revised answer ➜ references
#
# No string truncation, everything colour‑coded.
# """
#
# import datetime
# from typing import List
#
# from dotenv import load_dotenv
# load_dotenv()
#
# from rich.console import Console
# from rich.panel import Panel
# from rich.markdown import Markdown
# from rich.pretty import Pretty
#
# from langchain_core.output_parsers.openai_tools import (
#     JsonOutputToolsParser,
#     PydanticToolsParser,
# )
# from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_openai import ChatOpenAI
#
# from schemas import AnswerQuestion, ReviseAnswer
#
# # ─────────────────────────────────────────────────────────────────────────────
# # 🖥️  Console
# # ─────────────────────────────────────────────────────────────────────────────
# console = Console()
#
# # ─────────────────────────────────────────────────────────────────────────────
# # 🤖  LLM + Parsers
# # ─────────────────────────────────────────────────────────────────────────────
# llm = ChatOpenAI(model="gpt-4.1-mini")
#
# json_parser = JsonOutputToolsParser(return_id=True)
# answer_parser = PydanticToolsParser(tools=[AnswerQuestion])
# revise_parser = PydanticToolsParser(tools=[ReviseAnswer])
#
# # ─────────────────────────────────────────────────────────────────────────────
# # 📜  Prompt templates
# # ─────────────────────────────────────────────────────────────────────────────
# actor_template = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             """You are an expert researcher.\nCurrent time: {time}\n\n1. {first_instruction}\n2. Reflect and critique your answer. Be severe to maximize improvement.\n3. Recommend search queries to search information and improve your answer.""",
#         ),
#         MessagesPlaceholder(variable_name="messages"),
#         ("system", "Answer the user's question above using the required format."),
#     ]
# ).partial(time=lambda: datetime.datetime.now().isoformat())
#
# # Responder prompt
# responder_prompt = actor_template.partial(first_instruction="Provide a detailed ~250 words answer.")
# responder_chain = responder_prompt | llm.bind_tools(tools=[AnswerQuestion], tool_choice="AnswerQuestion")
#
# # Reviser prompt
# revise_instructions = (
#     "Revise your previous answer using the new information.\n"
#     "- Use the critique to add missing pieces.\n"
#     "- Remove superfluous detail and keep the answer under 250 words.\n"
#     "- Include numerical citations [1], [2], … inside the text.\n"
#     "- Append a 'References' list at the bottom."
# )
# reviser_prompt = actor_template.partial(first_instruction=revise_instructions)
# reviser_chain = reviser_prompt | llm.bind_tools(tools=[ReviseAnswer], tool_choice="ReviseAnswer")
#
# # ─────────────────────────────────────────────────────────────────────────────
# # 🚀  Flow runner
# # ─────────────────────────────────────────────────────────────────────────────
#
# def run_flow(question: str) -> None:
#     """Run the Responder → Reviser flow and pretty‑print every stage."""
#
#     console.rule("[bold green]Responder → Reviser Flow")
#
#     human_msg = HumanMessage(content=question)
#     console.print(Panel(Markdown(question), title="[bold cyan]User Question"))
#
#     # ── Responder ────────────────────────────────────────────────────────────
#     responder_raw = responder_chain.invoke({"messages": [human_msg]})
#     console.print(Panel(Pretty(json_parser.invoke(responder_raw), expand_all=True, max_string=10_000),
#                         title="[bold cyan]Responder • Raw Tool Call", expand=True))
#
#     responder_obj = answer_parser.invoke(responder_raw)
#     if isinstance(responder_obj, list):
#         responder_obj = responder_obj[0]
#
#     console.print(Panel(Markdown(responder_obj.answer), title="[bold cyan]Responder • Answer"))
#
#     reflect_md = (
#         f"**Missing:** {responder_obj.reflection.missing}\n\n"
#         f"**Superfluous:** {responder_obj.reflection.superfluous}"
#     )
#     console.print(Panel(Markdown(reflect_md), title="[bold cyan]Responder • Reflection"))
#
#     queries_md = "\n".join(f"- {q}" for q in responder_obj.search_queries)
#     console.print(Panel(Markdown(queries_md), title="[bold cyan]Responder • Search Queries"))
#
#     # ── Reviser ──────────────────────────────────────────────────────────────
#     history: List[BaseMessage] = [human_msg, AIMessage(content=responder_obj.answer)]
#
#     reviser_raw = reviser_chain.invoke({"messages": history})
#     console.print(Panel(Pretty(json_parser.invoke(reviser_raw), expand_all=True, max_string=10_000),
#                         title="[bold magenta]Reviser • Raw Tool Call", expand=True))
#
#     reviser_obj = revise_parser.invoke(reviser_raw)
#     if isinstance(reviser_obj, list):
#         reviser_obj = reviser_obj[0]
#
#     console.print(Panel(Markdown(reviser_obj.answer), title="[bold magenta]Reviser • Final Answer"))
#
#     refs_md = "\n".join(f"- {r}" for r in reviser_obj.reference)
#     console.print(Panel(Markdown(refs_md), title="[bold magenta]Reviser • References"))
#
#
# # ─────────────────────────────────────────────────────────────────────────────
# # 🏃‍♂️  Entry point
# # ─────────────────────────────────────────────────────────────────────────────
# if __name__ == "__main__":
#     sample_question = (
#         "Write about AI‑Powered SOC / autonomous problem domain, "
#         "list startups that do that and successfully raised capital."
#     )
#     run_flow(sample_question)


"""chains_reviser_print.py — Responder → Reviser demo with Rich panels

Shows:
1. User question
2. Responder raw tool‑call ▶ parsed answer / reflection / queries
3. Reviser raw tool‑call ▶ final answer ▶ references

Width is **not** frozen; Rich adapts to the current terminal size.
"""

import datetime
from typing import List

from dotenv import load_dotenv

load_dotenv()

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.output_parsers.openai_tools import (
    JsonOutputToolsParser,
    PydanticToolsParser,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.pretty import Pretty

from schemas import AnswerQuestion, ReviseAnswer

# ─────────────────────────────────────────────────────────────────────────────
# 🖥️  Console (dynamic width)
# ─────────────────────────────────────────────────────────────────────────────
console = Console()

# ─────────────────────────────────────────────────────────────────────────────
# 🤖  LLM + Parsers
# ─────────────────────────────────────────────────────────────────────────────
llm = ChatOpenAI(model="gpt-4.1-mini")

json_parser = JsonOutputToolsParser(return_id=True)
answer_parser = PydanticToolsParser(tools=[AnswerQuestion])
revise_parser = PydanticToolsParser(tools=[ReviseAnswer])

# ─────────────────────────────────────────────────────────────────────────────
# 📜  Prompt templates
# ─────────────────────────────────────────────────────────────────────────────
actor_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert researcher.\nCurrent time: {time}\n\n1. {first_instruction}\n2. Reflect and critique your answer. Be severe to maximize improvement.\n3. Recommend search queries to search information and improve your answer.""",
        ),
        MessagesPlaceholder(variable_name="messages"),
        ("system", "Answer the user's question above using the required format."),
    ]
).partial(time=lambda: datetime.datetime.now().isoformat())

# Responder prompt
responder_prompt = actor_template.partial(
    first_instruction="Provide a detailed ~250 words answer."
)
responder_chain = responder_prompt | llm.bind_tools(
    tools=[AnswerQuestion], tool_choice="AnswerQuestion"
)

# Reviser prompt
revise_instructions = (
    "Revise your previous answer using the critique above.\n"
    "- Add missing details and remove superfluous parts.\n"
    "- Keep it ≤250 words.\n"
    "- Use inline numeric citations [1], [2], …\n"
    "- Append a 'References' list at the bottom."
)
reviser_prompt = actor_template.partial(first_instruction=revise_instructions)
reviser_chain = reviser_prompt | llm.bind_tools(
    tools=[ReviseAnswer], tool_choice="ReviseAnswer"
)

# ─────────────────────────────────────────────────────────────────────────────
# 🚀  Flow runner
# ─────────────────────────────────────────────────────────────────────────────


def run_flow(question: str) -> None:
    """Run the Responder → Reviser flow and pretty‑print each stage."""

    console.rule("[bold green]Responder → Reviser Flow")

    human_msg = HumanMessage(content=question)
    console.print(Panel(Markdown(question), title="[bold cyan]User Question"))

    # ── Responder ────────────────────────────────────────────────────────────
    responder_raw = responder_chain.invoke({"messages": [human_msg]})
    console.print(
        Panel(
            Pretty(
                json_parser.invoke(responder_raw), expand_all=True, max_string=10_000
            ),
            title="[bold cyan]Responder • Raw Tool Call",
            expand=True,
        )
    )

    responder_obj = answer_parser.invoke(responder_raw)
    if isinstance(responder_obj, list):
        responder_obj = responder_obj[0]

    console.print(
        Panel(Markdown(responder_obj.answer), title="[bold cyan]Responder • Answer")
    )

    reflect_md = (
        f"**Missing:** {responder_obj.reflection.missing}\n\n"
        f"**Superfluous:** {responder_obj.reflection.superfluous}"
    )
    console.print(
        Panel(Markdown(reflect_md), title="[bold cyan]Responder • Reflection")
    )

    queries_md = "\n".join(f"- {q}" for q in responder_obj.search_queries)
    console.print(
        Panel(Markdown(queries_md), title="[bold cyan]Responder • Search Queries")
    )

    # ── Reviser ──────────────────────────────────────────────────────────────
    history: List[BaseMessage] = [human_msg, AIMessage(content=responder_obj.answer)]

    reviser_raw = reviser_chain.invoke({"messages": history})
    console.print(
        Panel(
            Pretty(json_parser.invoke(reviser_raw), expand_all=True, max_string=10_000),
            title="[bold magenta]Reviser • Raw Tool Call",
            expand=True,
        )
    )

    # Robust parsing with graceful fallback on schema drift
    from pydantic_core import ValidationError

    try:
        reviser_obj = revise_parser.invoke(reviser_raw)
        if isinstance(reviser_obj, list):
            reviser_obj = reviser_obj[0]
        answer_text = reviser_obj.answer
        refs: List[str] = getattr(reviser_obj, "reference", [])
    except (ValidationError, KeyError, TypeError):
        raw_dict = json_parser.invoke(reviser_raw)[0]["args"]
        answer_text = raw_dict.get("answer", "<missing answer>")
        refs = raw_dict.get("reflection", {}).get("reference", [])

    console.print(
        Panel(Markdown(answer_text), title="[bold magenta]Reviser • Final Answer")
    )

    if refs:
        refs_md = "\n".join(f"- {r}" for r in refs)
        console.print(
            Panel(Markdown(refs_md), title="[bold magenta]Reviser • References")
        )


# ─────────────────────────────────────────────────────────────────────────────
# 🏃‍♂️  Entry point
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    sample_question = (
        "Write about AI‑Powered SOC / autonomous problem domain, "
        "list startups that do that and successfully raised capital."
    )
    run_flow(sample_question)
