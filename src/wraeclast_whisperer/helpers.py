import os

import jinja2


def render_template(template_name: str = "instructions.jinja") -> str:
    # Get the directory of the current script
    file_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the path to the templates directory
    templates_dir = os.path.join(file_dir, "..", "..", "templates")
    # Load and render the instructions template
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(templates_dir))
    template = env.get_template(template_name)
    instructions = template.render()
    return instructions
