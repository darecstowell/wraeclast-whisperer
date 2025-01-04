from abc import ABC, abstractmethod
from typing import Any, Type

import pydantic
from mediawiki import MediaWiki
from pydantic import BaseModel

# TODO: Move these to a config file
poe2wiki = MediaWiki(
    url="https://www.poe2wiki.net/api.php",
    user_agent="wraeclast-whisperer/0.0.1 (https://github.com/darecstowell) python-pymediawiki/0.7.4",
)


class AssistantTool(BaseModel, ABC):
    name: str
    friendly_name: str = ""
    description: str = ""
    strict: bool = True
    parallel_tool_calls: bool = False
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
