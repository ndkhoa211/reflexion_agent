from dotenv import load_dotenv

load_dotenv()


from typing import List
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from langchain_core.messages import BaseMessage, ToolMessage
from langgraph.graph import END, MessageGraph

from chains import first_responder, reviser
from tool_executor import execute_tools

# these classes are going to populate our state objects in our graph


MAX_ITERATIONS = 3
builder = MessageGraph()
builder.add_node("draft", first_responder)
builder.add_node("execute_tools", execute_tools)
builder.add_node("reviser", reviser)
builder.add_edge("draft", "execute_tools")
builder.add_edge("execute_tools", "reviser")


# at "reviser" node, this function decides which node we're going to next
def event_loop(state: List[BaseMessage]) -> str:
    # execute_tools isn't a vanilla function, but a tool node whose outputs are ToolMessage instances.
    # the state list of messages you inspect will therefore contain those ToolMessage objects
    # corresponding to each tool invocation
    count_tool_visits = sum(isinstance(item, ToolMessage) for item in state)
    num_iterations = count_tool_visits
    if num_iterations > MAX_ITERATIONS:
        return END  # go to END node
    return "execute_tools"  # go to "execute_tools" node


# conditional edge at the "reviser" node
builder.add_conditional_edges(
    "reviser", event_loop, {END: END, "execute_tools": "execute_tools"}
)

# define the graph's entry point
builder.set_entry_point("draft")

# compile to get a runnable graph
graph = builder.compile()

# export mermaid graph in .png
graph.get_graph().draw_mermaid_png(output_file_path="reflexion_agent.png")


console = Console()


if __name__ == "__main__":
    print("Hello Reflexion Agent!")

    # invoke the graph
    res = graph.invoke(
        "Write about AI-Powered SOC / autonomous problem domain, "
        "list startups that do that and successfully raised capital."
    )
    res = graph.invoke("Write about Group Cohomology, list recent researches about it.")

    # print(res[-1].tool_calls[0]["args"]["answer"])
    # Pretty‑print the answer with Rich 🎨
    answer = res[-1].tool_calls[0]["args"]["answer"]
    console.print(
        Panel(
            Markdown(answer),
            title="💡 Final Answer",
            border_style="green",
            expand=True,
        )
    )
