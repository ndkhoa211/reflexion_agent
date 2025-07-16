# this file holds the schemas for the output we want
# i.e. ensure that output we get from LLM is in a structured format
# the format:
# 1. response/answer field: have the original essay
# 2. critique/reflect field: critique for the essay
# 3. search field: a list of values we should search for


from typing import List

from pydantic import BaseModel, Field


class Reflection(BaseModel):
    missing: str = Field(description="Critique of what is missing.")
    superfluous: str = Field(description="Critique of what is superfluous.")


# important note: this Reflection class is going to be used alongside with
# the function calling feature, it'll ground the response from LLM to fill
# up those values -> give us a very concise feedback from LLM


# transform "Responder" agent's output into a pydantic object
class AnswerQuestion(BaseModel):
    """Answer the question."""

    answer: str = Field(description="250 words detailed answer to the question.")
    # a Reflection object
    # this is a cool trick where we actually prompt LLM through description of the class' fields
    reflection: Reflection = Field(description="Your reflection on the initial answer.")
    search_queries: List[str] = Field(
        description="1-3 search queries for researching improvements to address the critique of your current answer."
    )


# inherited from AnswerQuestion
class ReviseAnswer(AnswerQuestion):
    """Revise your original answer to your question."""

    reference: List[str] = Field(
        description="Citations motivating your updated answer."
    )
