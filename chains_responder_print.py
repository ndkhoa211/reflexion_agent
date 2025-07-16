# import datetime
# from dotenv import load_dotenv
#
# load_dotenv()
#
# from rich.console import Console
# from rich.panel import Panel
# from rich.markdown import Markdown
# from rich.json import JSON
#
# from langchain_core.output_parsers.openai_tools import (
#     JsonOutputToolsParser,
#     PydanticToolsParser,
# )
# from langchain_core.messages import HumanMessage
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_openai import ChatOpenAI
#
# from schemas import AnswerQuestion, Reflection  # local pydantic models
#
# # ----------------------------------------------------------------------------
# # 🖥️  Console setup
# # ----------------------------------------------------------------------------
# console = Console()
#
# # ----------------------------------------------------------------------------
# # 🤖  LLM + Parsers setup
# # ----------------------------------------------------------------------------
# llm = ChatOpenAI(model="gpt-4.1-mini")
#
# json_parser = JsonOutputToolsParser(return_id=True)
# pydantic_parser = PydanticToolsParser(tools=[AnswerQuestion])
#
# # ----------------------------------------------------------------------------
# # 📜  Prompt templates
# # ----------------------------------------------------------------------------
# actor_prompt_template = ChatPromptTemplate.from_messages(
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
# first_responder_prompt_template = actor_prompt_template.partial(
#     first_instruction="Provide a detailed ~250 words answer."
# )
#
# first_responder_chain = (
#     first_responder_prompt_template
#     | llm.bind_tools(tools=[AnswerQuestion], tool_choice="AnswerQuestion")
# )
#
# # ----------------------------------------------------------------------------
# # 🚀  Helper
# # ----------------------------------------------------------------------------
#
# def run_demo() -> None:
#     """Run a demo Q→A flow and pretty‑print every stage."""
#
#     # 1️⃣  Compose the user question.
#     human_message = HumanMessage(
#         content=(
#             "Write about AI‑Powered SOC / autonomous problem domain, "
#             "list startups that do that and successfully raised capital."
#         )
#     )
#
#     console.rule("[bold green]Flow: User ➜ Prompt ➜ LLM ➜ Parsed")
#     console.print(Panel(Markdown(human_message.content), title="[bold]User Question"))
#
#     # 2️⃣  Call the LLM — returns a *ChatMessage* that triggers the tool.
#     raw_result = first_responder_chain.invoke({"messages": [human_message]})
#
#     # 3️⃣  Show the raw JSON tool‑call (function name & arguments).
#     raw_json = json_parser.invoke(raw_result)
#     console.print(Panel(JSON.from_data(raw_json), title="[bold]Raw LLM Tool Call"))
#
#     # 4️⃣  Parse the tool‑call into our strongly‑typed pydantic model.
#     parsed_result = pydantic_parser.invoke(raw_result)
#     if isinstance(parsed_result, list):
#         if not parsed_result:
#             raise ValueError("Pydantic parser returned an empty list – no tool calls found.")
#         parsed: AnswerQuestion = parsed_result[0]
#     else:
#         parsed: AnswerQuestion = parsed_result  # type: ignore[arg-type]
#
#     # 5️⃣  Pretty‑print each section.
#     console.print(Panel(Markdown(parsed.answer), title="[bold]Answer"))
#
#     reflection_md = (
#         f"**Missing:** {parsed.reflection.missing}\n\n"
#         f"**Superfluous:** {parsed.reflection.superfluous}"
#     )
#     console.print(Panel(Markdown(reflection_md), title="[bold]Reflection"))
#
#     queries_md = "\n".join(f"- {q}" for q in parsed.search_queries)
#     console.print(Panel(Markdown(queries_md), title="[bold]Suggested Search Queries"))
#
#
# # ----------------------------------------------------------------------------
# # 🏃‍♂️  Entry‑point
# # ----------------------------------------------------------------------------
# if __name__ == "__main__":
#     run_demo()



import datetime
from dotenv import load_dotenv

load_dotenv()

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.pretty import Pretty  # ⬅️ pretty‑printer that never truncates

from langchain_core.output_parsers.openai_tools import (
    JsonOutputToolsParser,
    PydanticToolsParser,
)
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from schemas import AnswerQuestion, Reflection  # local pydantic models

# ----------------------------------------------------------------------------
# 🖥️  Console setup
# ----------------------------------------------------------------------------
console = Console()

# ----------------------------------------------------------------------------
# 🤖  LLM + Parsers setup
# ----------------------------------------------------------------------------
llm = ChatOpenAI(model="gpt-4.1-mini")

json_parser = JsonOutputToolsParser(return_id=True)
pydantic_parser = PydanticToolsParser(tools=[AnswerQuestion])

# ----------------------------------------------------------------------------
# 📜  Prompt templates
# ----------------------------------------------------------------------------
actor_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert researcher.\nCurrent time: {time}\n\n1. {first_instruction}\n2. Reflect and critique your answer. Be severe to maximize improvement.\n3. Recommend search queries to search information and improve your answer.""",
        ),
        MessagesPlaceholder(variable_name="messages"),
        ("system", "Answer the user's question above using the required format."),
    ]
).partial(time=lambda: datetime.datetime.now().isoformat())

first_responder_prompt_template = actor_prompt_template.partial(
    first_instruction="Provide a detailed ~250 words answer."
)

first_responder_chain = (
    first_responder_prompt_template
    | llm.bind_tools(tools=[AnswerQuestion], tool_choice="AnswerQuestion")
)

# ----------------------------------------------------------------------------
# 🚀  Helper
# ----------------------------------------------------------------------------

def run_demo() -> None:
    """Run a demo Q→A flow and pretty‑print every stage."""

    # 1️⃣  Compose the user question.
    human_message = HumanMessage(
        content=(
            "Write about AI‑Powered SOC / autonomous problem domain, "
            "list startups that do that and successfully raised capital."
        )
    )

    console.rule("[bold green]Flow: User ➜ Prompt ➜ LLM ➜ Parsed")
    console.print(Panel(Markdown(human_message.content), title="[bold]User Question"))

    # 2️⃣  Call the LLM — returns a *ChatMessage* that triggers the tool.
    raw_result = first_responder_chain.invoke({"messages": [human_message]})

    # 3️⃣  Show the raw JSON tool‑call (function name & arguments) *without truncation*.
    raw_json = json_parser.invoke(raw_result)
    pretty_json = Pretty(raw_json, expand_all=True, max_string=10_000)
    console.print(Panel(pretty_json, title="[bold]Raw LLM Tool Call", expand=True))

    # 4️⃣  Parse the tool‑call into our strongly‑typed pydantic model.
    parsed_result = pydantic_parser.invoke(raw_result)
    if isinstance(parsed_result, list):
        if not parsed_result:
            raise ValueError("Pydantic parser returned an empty list – no tool calls found.")
        parsed: AnswerQuestion = parsed_result[0]
    else:
        parsed: AnswerQuestion = parsed_result  # type: ignore[arg-type]

    # 5️⃣  Pretty‑print each section.
    console.print(Panel(Markdown(parsed.answer), title="[bold]Answer"))

    reflection_md = (
        f"**Missing:** {parsed.reflection.missing}\n\n"
        f"**Superfluous:** {parsed.reflection.superfluous}"
    )
    console.print(Panel(Markdown(reflection_md), title="[bold]Reflection"))

    queries_md = "\n".join(f"- {q}" for q in parsed.search_queries)
    console.print(Panel(Markdown(queries_md), title="[bold]Suggested Search Queries"))


# ----------------------------------------------------------------------------
# 🏃‍♂️  Entry‑point
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    run_demo()

