import unittest
from unittest.mock import Mock

from moose_benchmark.contracts import StrictModel
from moose_benchmark.llm import EvaluatorInfrastructureError, LLMClient, LLMConfig


class ExampleOutput(StrictModel):
    value: str


class LLMClientTests(unittest.TestCase):
    def test_routes_all_supported_providers(self):
        cases = [
            ("openai", None, "_generate_openai"),
            ("claude", None, "_generate_claude"),
            ("litellm", "http://proxy.example/v1", "_generate_openai"),
            ("ollama", None, "_generate_ollama"),
        ]
        for provider, base_url, method_name in cases:
            with self.subTest(provider=provider):
                client = LLMClient(
                    LLMConfig(
                        provider=provider,
                        model="judge",
                        base_url=base_url,
                    )
                )
                method = Mock(return_value='{"value":"ok"}')
                setattr(client, method_name, method)
                result = client.generate_structured(
                    system_prompt="system",
                    user_prompt="user",
                    response_model=ExampleOutput,
                )
                self.assertEqual(result.output.value, "ok")
                method.assert_called_once()

    def test_retries_invalid_structured_output_once(self):
        client = LLMClient(LLMConfig(provider="ollama", model="judge", max_retries=1))
        client._generate = Mock(side_effect=['{"wrong":"shape"}', '{"value":"ok"}'])  # noqa: SLF001
        result = client.generate_structured(
            system_prompt="system",
            user_prompt="user",
            response_model=ExampleOutput,
        )
        self.assertEqual(result.output.value, "ok")
        self.assertEqual(client._generate.call_count, 2)  # noqa: SLF001

    def test_exhausted_retries_raise_infrastructure_error(self):
        client = LLMClient(LLMConfig(provider="ollama", model="judge", max_retries=1))
        client._generate = Mock(return_value="not-json")  # noqa: SLF001
        with self.assertRaisesRegex(EvaluatorInfrastructureError, "semantic judge failed"):
            client.generate_structured(
                system_prompt="system",
                user_prompt="user",
                response_model=ExampleOutput,
            )

    def test_provider_transport_failures_are_infrastructure_errors(self):
        cases = [
            ("openai", None, "_generate_openai"),
            ("claude", None, "_generate_claude"),
            ("litellm", "http://proxy.example/v1", "_generate_openai"),
            ("ollama", None, "_generate_ollama"),
        ]
        for provider, base_url, method_name in cases:
            with self.subTest(provider=provider):
                client = LLMClient(
                    LLMConfig(
                        provider=provider,
                        model="judge",
                        base_url=base_url,
                        max_retries=0,
                    )
                )
                setattr(client, method_name, Mock(side_effect=ConnectionError("offline")))
                with self.assertRaises(EvaluatorInfrastructureError):
                    client.generate_structured(
                        system_prompt="system",
                        user_prompt="user",
                        response_model=ExampleOutput,
                    )

    def test_litellm_requires_base_url(self):
        with self.assertRaisesRegex(ValueError, "base_url"):
            LLMConfig(provider="litellm", model="judge")


if __name__ == "__main__":
    unittest.main()
