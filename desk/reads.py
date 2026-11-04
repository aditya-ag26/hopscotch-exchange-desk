from langchain_core.prompts import PromptTemplate

from desk.config import llm
from desk.state import Claim, DeskState, Tone

llm_claim = llm.with_structured_output(Claim)
llm_tone = llm.with_structured_output(Tone)


def extract_claim(state: DeskState):
    tem = PromptTemplate(
        template="Read this Hopscotch customer message and extract the claim: {message}",
        input_variables=["message"],
    )
    chain = tem | llm_claim
    claim = chain.invoke({"message": state["message"]})
    return {"claim": claim.model_dump()}


def read_tone(state: DeskState):
    tem = PromptTemplate(
        template="How does this customer sound? Message: {message}",
        input_variables=["message"],
    )
    chain = tem | llm_tone
    result = chain.invoke({"message": state["message"]})
    return {"tone": result.tone}


if __name__ == "__main__":
    message = "Order HS2291. The 4-5Y kurta set is too small. Please pick it up from 122002."
    print(extract_claim({"message": message}))
    print(read_tone({"message": message}))
