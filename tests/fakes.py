from moose_benchmark.evaluators.semantic import (
    JudgeCriterionResult,
    SemanticJudgeOutput,
)
from moose_benchmark.llm import StructuredGeneration


class ScriptedLLMClient:
    def __init__(self, ratings):
        self.ratings = ratings
        self.last_system_prompt = None
        self.last_user_prompt = None

    def generate_structured(self, *, system_prompt, user_prompt, response_model):
        self.last_system_prompt = system_prompt
        self.last_user_prompt = user_prompt
        output = SemanticJudgeOutput(
            criteria=[
                JudgeCriterionResult(
                    id=criterion_id,
                    rating=rating,
                    rationale=f"scripted {rating}",
                    response_evidence=[],
                )
                for criterion_id, rating in self.ratings.items()
            ]
        )
        return StructuredGeneration(
            output=response_model.model_validate(output.model_dump(mode="json")),
            provider="fixture",
            model="scripted-judge",
            configuration_sha256="1" * 64,
            request_sha256="2" * 64,
            response_sha256="3" * 64,
        )
