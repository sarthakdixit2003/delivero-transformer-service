import logging
from typing import Dict, List
from pydantic import BaseModel
from app.modules.transformer.dto import RuleSchema
from app.modules.transformer.engine.executor import (
    execute_transform,
    execute_validation,
)
from app.modules.transformer.error_collector import Error, ErrorCollector
from app.modules.transformer.schema import JSONValue

logger = logging.getLogger(__name__)


class TransformerServiceOutput(BaseModel):
    transformed_payload: Dict[str, JSONValue]
    errors: List[Error]


class TransformerService:
    def __init__(self, payload: JSONValue, rule: RuleSchema):
        self.payload = payload
        self.rule = rule

    def transformPayload(self) -> TransformerServiceOutput:
        errors = ErrorCollector()
        logger.info(f"Transforming payload: {self.payload}")
        executor_output = execute_transform(
            self.payload, self.rule.transform_template, errors
        )
        logger.info(f"Validating payload: {executor_output.transformed_payload}")
        execute_validation(
            executor_output.transformed_payload, self.rule.validation_schema, errors
        )
        logger.info(f"Validation errors: {errors.get()}")
        return TransformerServiceOutput(
            transformed_payload=executor_output.transformed_payload, errors=errors.get()
        )
