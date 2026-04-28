from typing import Dict, List
from pydantic import BaseModel
from app.modules.transformer.dto import RuleSchema
from app.modules.transformer.engine.executor import execute_transform
from app.modules.transformer.error_collector import Error, ErrorCollector
from app.modules.transformer.schema import JSONValue


class TransformerServiceOutput(BaseModel):
    transformed_payload: Dict[str, JSONValue]
    errors: List[Error]


class TransformerService:
    def __init__(self, payload: JSONValue, rule: RuleSchema):
        self.payload = payload
        self.rule = rule

    def transformPayload(self) -> TransformerServiceOutput:
        errors = ErrorCollector()

        executor_output = execute_transform(
            self.payload, self.rule.transform_template, errors
        )
        return TransformerServiceOutput(
            transformed_payload=executor_output.transformed_payload, errors=errors.get()
        )
