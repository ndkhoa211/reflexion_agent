import datetime
from dotenv import load_dotenv
load_dotenv()


from langchain_core.output_parsers.openai_tools import (
    JsonOutputToolsParser,
    PydanticToolsParser,
)
from langchain_core.messages import HumanMessage
from langchain_core.prompts import (ChatPromptTemplate, # hold history of agent iterations
                                    MessagesPlaceholder)
from langchain_openai import ChatOpenAI


from schemas import AnswerQuestion


llm = ChatOpenAI(model="gpt-4.1-mini")

# create 2 output parsers
parser = JsonOutputToolsParser(return_id=True) # return function call from LLM and transform into a dict
parser_pydantic = PydanticToolsParser(tools=[AnswerQuestion]) #take response from LLM, then transform it into AnswerQuestion object

# RECALL:
# the input for this "Responder" agent/node is the topic we want to write about
# and the agent is going to write for us the initial response
# now, in the answer of the agent we need:
# 1. the content, i.e.  first draft of the article,
# 2. some criticism on the newly created article,
# 3. and some search terms that will enhance the article.


# main prompt of Actor (agent)
# this prompt template is also used by "Reviser" agent/node,
# which takes all the information to rewrite the article.
actor_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert researcher.
Current time: {time}

1. {first_instruction}
2. Reflect and critique your answer. Be severe to maximize improvement.
3. Recommend search queries to search information and improve your answer.""",
        ),
        MessagesPlaceholder(variable_name="messages"), # placeholder for human_message
        ("system", "Answer the user's question above using the required format."),
    ]
).partial( # populate some already known placeholders, in this case: {time}
    time=lambda: datetime.datetime.now().isoformat(), # date with ISO format
)
# structure of the format:
# prompt = [
#     ("system", "you are an..."),
#     ("messages", "history chat"),
#     ("system", "Answer the user's question..."),
# ]


# populate field: {first_instruction}
first_responder_prompt_template = actor_prompt_template.partial(
    first_instruction="Provide a detailed ~250 words answer.",
)


# create "first_responder" chain
# bind LLM with AnswerQuestion object as a tool for tool calling
# tool_choice="AnswerQuestion" forces LLM to always use AnswerQuestion tool,
# thus grounding the response to the object that we want to receive
# also pipe first_responder_prompt_template into LLM
first_responder = (
        first_responder_prompt_template
        | llm.bind_tools(tools=[AnswerQuestion],
                         tool_choice="AnswerQuestion")
)





if __name__ == "__main__":

    # create a chain
    human_message = HumanMessage(
        content="Write about AI-Powered SOC / autonomous problem domain,"
        "list startups that do that and successfully raised capital."
    )
    chain = (
        first_responder_prompt_template
        | llm.bind_tools(tools=[AnswerQuestion],
                         tool_choice="AnswerQuestion")
        | parser_pydantic # parse response as a pydantic object of AnswerQuestion
    )


    # invoke the chain
    res = chain.invoke(input={"messages": [human_message]})
    print(res)