from pathlib import Path

import toml
from fastapi.routing import APIRoute


def use_handler_name_as_unique_id(route: APIRoute) -> str:
    return f"{route.name}"


def get_project_config(base_dir: Path) -> dict[str, str]:
    with open(base_dir / "pyproject.toml", "r") as file:
        config = toml.load(file).get("project", {})
        project_name = config["name"]
        project_version = config["version"]
        project_description = config["description"]
        return {
            "name": project_name,
            "version": project_version,
            "description": project_description,
        }
