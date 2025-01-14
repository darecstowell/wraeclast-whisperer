import os

import jinja2


def render_template(template_name: str, context: dict | None = {}) -> str:
    """
    Render a template using Jinja2 and return the rendered string
    """
    file_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(file_dir, "..", "..", "templates")
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(templates_dir))
    template = env.get_template(template_name)
    instructions = template.render(context)
    return instructions
