from pydantic import BaseModel


class HelloWorldParameters(BaseModel):
    # No parameters needed
    pass


class GetCurrentTemperatureParameters(BaseModel):
    # No parameters needed
    pass


# TODO: create parent tool class and define all this in a pydantic model
def get_tools():
    return [
        {
            "type": "function",
            "function": {
                "name": "hello_world",
                "description": "Returns a greeting message.",
                "parameters": HelloWorldParameters.model_json_schema(),
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_current_temperature",
                "description": "Returns the current temperature.",
                "parameters": GetCurrentTemperatureParameters.model_json_schema(),
            },
        },
    ]


async def hello_world():
    """
    Returns a greeting message.
    """

    print("Called hello_world")
    return "hello world"


async def get_current_temperature():
    """
    Returns the current temperature
    """

    print("Called get_current_temperature")
    return "The current temperature is 72°F."
