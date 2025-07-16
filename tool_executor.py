from dotenv import load_dotenv

load_dotenv()

from langchain_core.tools import (
    StructuredTool,
)  # allow us to convert a Python function into a tool that can be used by LLM
from langchain_tavily import TavilySearch
from langgraph.prebuilt import ToolNode  # a node in LAngGraph we can invoke

from schemas import AnswerQuestion, ReviseAnswer

# it takes a function and provides to LLM a structured schema for the function,
# which helps LLM understand how to use the tool


# it's going to look at the state for the "messages" key, check the last message,
# and then see if there are any tool calls that were decided by LLM,
# if there are, it executes those tools for us in parallel.


# a langchain tool with the function of the search engine
tavily_tool = TavilySearch(max_results=5)
# but we don't want to use it as it is, like we usually do
# we want to do a cool trick here
# we'll take the original Tavily tool and its functionality and create from
# it 2 different tools with the same functionality of the Tavily search, but
# they have different names because they serve different purposes in the application workflow:
# AnswerQuestion tool: used during initial research phase when the agent is first answering the question.
# ReviseAnswer tool: used during the revision phase when the agent is improving its answer based on the reflection.
# that's why we need AnswerQuestion and ReviseAnswer objects because we want to get
# their names in order to label those tools.
# Theoretically, we can use one tool, but having separate names in two separate tools
# allows the system to clearly TRACE with stage of the research process triggered the search
# initial research vs. revision research
# it's going to help us in debugging and evaluating the response


def run_queries(search_queries: list[str], **kwargs):
    """Run the generated queries"""
    return tavily_tool.batch([{"query": query} for query in search_queries])
    # iterate over the queries and run concurrently with batch() function


# create a ToolNode object
execute_tool = ToolNode(
    [
        StructuredTool.from_function(run_queries, name=AnswerQuestion.__name__),
        StructuredTool.from_function(run_queries, name=ReviseAnswer.__name__),
    ]
)
