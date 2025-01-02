from abc import ABC, abstractmethod
from typing import Any, Type

import pydantic
from pydantic import BaseModel


class AssistantTool(BaseModel, ABC):
    name: str
    description: str = ""
    strict: bool = True
    parameters: Type[pydantic.BaseModel]

    @abstractmethod
    def run(self, **kwargs) -> Any:
        """Execute the tool with the given parameters."""
        pass

    @property
    def function_schema(self) -> dict:
        """
        Generate a FunctionDefinition object from the tool's parameters.
        """
        params_schema = self.parameters.model_json_schema()
        for parameter in params_schema["properties"].values():
            parameter.pop("title", None)
        params_schema.pop("title", None)
        params_schema["additionalProperties"] = False
        return {
            "name": self.name,
            "description": self.description,
            "parameters": params_schema,
            "strict": self.strict,
        }
