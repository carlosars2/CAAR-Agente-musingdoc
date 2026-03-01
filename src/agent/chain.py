from langchain_anthropic import ChatAnthropic
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from src.agent.prompt import SYSTEM_PROMPT
from src.config import ANTHROPIC_API_KEY, MODEL_NAME, MEMORY_WINDOW_SIZE


def create_llm() -> ChatAnthropic:
    return ChatAnthropic(
        model=MODEL_NAME,
        anthropic_api_key=ANTHROPIC_API_KEY,
        max_tokens=1024,
        temperature=0.3,
    )


def create_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ])


def create_memory() -> ConversationBufferWindowMemory:
    return ConversationBufferWindowMemory(
        k=MEMORY_WINDOW_SIZE,
        return_messages=True,
        memory_key="history",
    )


class AgentChain:
    """Manages a conversation chain with memory per session."""

    def __init__(self):
        self._sessions: dict[str, ConversationBufferWindowMemory] = {}
        self._llm = create_llm()
        self._prompt = create_prompt()
        self._chain = self._prompt | self._llm | StrOutputParser()

    def _get_memory(self, session_id: str) -> ConversationBufferWindowMemory:
        if session_id not in self._sessions:
            self._sessions[session_id] = create_memory()
        return self._sessions[session_id]

    async def chat(self, session_id: str, message: str) -> str:
        memory = self._get_memory(session_id)
        history = memory.load_memory_variables({}).get("history", [])

        response = await self._chain.ainvoke({
            "history": history,
            "input": message,
        })

        memory.save_context(
            {"input": message},
            {"output": response},
        )

        return response

    def clear_session(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)


# Singleton instance
agent_chain = AgentChain()
