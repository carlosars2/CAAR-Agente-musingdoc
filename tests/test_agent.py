import pytest
from unittest.mock import AsyncMock, patch

from src.agent.prompt import SYSTEM_PROMPT
from src.agent.tools import (
    get_pricing,
    get_cooperative_discount,
    is_supported_specialty,
    SPECIALTIES,
)


# --- System Prompt Tests ---

class TestSystemPrompt:
    def test_prompt_is_not_empty(self):
        assert len(SYSTEM_PROMPT) > 0

    def test_prompt_contains_identity(self):
        assert "Doc" in SYSTEM_PROMPT
        assert "Musing Doc" in SYSTEM_PROMPT

    def test_prompt_contains_all_agents(self):
        agents = [
            "Agente de Triagem",
            "Agente de Agendamento",
            "Agente de Cobrança",
            "Agente de Gestão",
            "Agente de Estoque",
            "Agente de Faturamento",
            "Agente de Compliance",
        ]
        for agent in agents:
            assert agent in SYSTEM_PROMPT, f"Missing agent: {agent}"

    def test_prompt_does_not_contain_packages(self):
        # Packages were removed — agent should never mention them
        lines = SYSTEM_PROMPT.split("\n")
        for i, line in enumerate(lines):
            # Allow the line that says "JAMAIS mencione nomes de pacotes"
            if "JAMAIS" in line:
                continue
            assert "Starter" not in line, f"Found 'Starter' on line {i+1}"
            assert "Enterprise" not in line or "Standard" in line or "Predictive" in line, \
                f"Found 'Enterprise' as package on line {i+1}"

    def test_prompt_does_not_contain_prices(self):
        assert "R$497" not in SYSTEM_PROMPT
        assert "R$1.297" not in SYSTEM_PROMPT
        assert "R$25.000" not in SYSTEM_PROMPT
        assert "R$180.000" not in SYSTEM_PROMPT
        assert "R$490" not in SYSTEM_PROMPT
        assert "R$890" not in SYSTEM_PROMPT
        assert "R$590" not in SYSTEM_PROMPT

    def test_prompt_says_personalized(self):
        assert "personalizada" in SYSTEM_PROMPT or "personalizado" in SYSTEM_PROMPT

    def test_prompt_contains_cooperative_model(self):
        assert "cooperativa" in SYSTEM_PROMPT.lower()

    def test_prompt_contains_funnel_stages(self):
        assert "Etapa 1" in SYSTEM_PROMPT
        assert "Etapa 5" in SYSTEM_PROMPT
        assert "100% grátis" in SYSTEM_PROMPT

    def test_prompt_contains_specialties(self):
        for specialty in SPECIALTIES:
            assert specialty in SYSTEM_PROMPT, f"Missing specialty: {specialty}"

    def test_prompt_contains_monetize_program(self):
        assert "Monetize" in SYSTEM_PROMPT or "MONETIZE" in SYSTEM_PROMPT
        assert "70%" in SYSTEM_PROMPT
        assert "30%" in SYSTEM_PROMPT

    def test_prompt_contains_escalation_rules(self):
        assert "ESCALAR PARA HUMANO" in SYSTEM_PROMPT

    def test_prompt_contains_behavior_rules(self):
        assert "NUNCA" in SYSTEM_PROMPT
        assert "SEMPRE" in SYSTEM_PROMPT


# --- Tools Tests ---

class TestPricing:
    def test_get_starter_pricing(self):
        plan = get_pricing("starter")
        assert plan is not None
        assert plan["price"] == 497
        assert plan["agents"] == 2

    def test_get_pro_pricing(self):
        plan = get_pricing("pro")
        assert plan is not None
        assert plan["price"] == 1297
        assert plan["agents"] == 5

    def test_get_enterprise_pricing(self):
        plan = get_pricing("enterprise")
        assert plan is not None
        assert plan["price"] is None
        assert plan["agents"] == 7

    def test_get_invalid_plan(self):
        assert get_pricing("invalid") is None

    def test_case_insensitive(self):
        assert get_pricing("Starter") is not None
        assert get_pricing("PRO") is not None


class TestCooperativeDiscount:
    def test_2_members(self):
        assert get_cooperative_discount(2) == 0.15

    def test_3_members(self):
        assert get_cooperative_discount(3) == 0.15

    def test_5_members(self):
        assert get_cooperative_discount(5) == 0.25

    def test_8_members(self):
        assert get_cooperative_discount(8) == 0.35

    def test_1_member_no_discount(self):
        assert get_cooperative_discount(1) == 0.0

    def test_11_members_no_discount(self):
        assert get_cooperative_discount(11) == 0.0


class TestSpecialties:
    def test_supported_specialty(self):
        assert is_supported_specialty("Odontologia") is True
        assert is_supported_specialty("Cardiologia") is True

    def test_partial_match(self):
        assert is_supported_specialty("odonto") is True
        assert is_supported_specialty("cardio") is True

    def test_unsupported_specialty(self):
        assert is_supported_specialty("Engenharia") is False

    def test_all_14_specialties(self):
        assert len(SPECIALTIES) == 14


# --- API Tests ---

class TestChatEndpoint:
    @pytest.mark.asyncio
    async def test_chat_returns_response(self):
        from src.api.chat import chat, ChatRequest

        mock_response = "Olá! Sou o Doc, assistente da Musing Doc."

        with patch("src.api.chat.agent_chain") as mock_chain:
            mock_chain.chat = AsyncMock(return_value=mock_response)

            request = ChatRequest(session_id="test-1", message="Olá")
            response = await chat(request)

            assert response.response == mock_response
            assert response.session_id == "test-1"
            mock_chain.chat.assert_awaited_once_with(
                session_id="test-1",
                message="Olá",
            )

    @pytest.mark.asyncio
    async def test_chat_rejects_empty_message(self):
        from fastapi import HTTPException
        from src.api.chat import chat, ChatRequest

        request = ChatRequest(session_id="test-1", message="   ")

        with pytest.raises(HTTPException) as exc_info:
            await chat(request)

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_chat_rejects_empty_session(self):
        from fastapi import HTTPException
        from src.api.chat import chat, ChatRequest

        request = ChatRequest(session_id="   ", message="Olá")

        with pytest.raises(HTTPException) as exc_info:
            await chat(request)

        assert exc_info.value.status_code == 400


# --- Chain Tests ---

class TestAgentChain:
    def test_chain_creates_memory_per_session(self):
        from src.agent.chain import AgentChain

        chain = AgentChain()
        mem1 = chain._get_memory("session-a")
        mem2 = chain._get_memory("session-b")
        mem1_again = chain._get_memory("session-a")

        assert mem1 is not mem2
        assert mem1 is mem1_again

    def test_clear_session(self):
        from src.agent.chain import AgentChain

        chain = AgentChain()
        chain._get_memory("session-x")
        assert "session-x" in chain._sessions

        chain.clear_session("session-x")
        assert "session-x" not in chain._sessions

    def test_clear_nonexistent_session(self):
        from src.agent.chain import AgentChain

        chain = AgentChain()
        chain.clear_session("nonexistent")  # should not raise
