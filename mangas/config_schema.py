"""Validates config.yaml on startup using jsonschema."""
import jsonschema

CONFIG_SCHEMA = {
    "type": "object",
    "required": ["schedules", "sites", "themes", "recommendations", "web"],
    "properties": {
        "schedules": {
            "type": "object",
            "required": ["chapter_check", "recommendations"],
            "properties": {
                "chapter_check": {"type": "string"},
                "recommendations": {"type": "string"},
            },
        },
        "sites": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "required": ["scraper", "crawler"],
                "properties": {
                    "scraper": {"type": "boolean"},
                    "crawler": {"type": "boolean"},
                    "domains": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
        "themes": {"type": "array", "items": {"type": "string"}},
        "recommendations": {
            "type": "object",
            "required": ["min_chapters"],
            "properties": {
                "min_chapters": {"type": "integer", "minimum": 1},
                "max_pages": {"type": "integer", "minimum": 1, "maximum": 50},
            },
        },
        "web": {
            "type": "object",
            "required": ["port", "host"],
            "properties": {
                "port": {"type": "integer"},
                "host": {"type": "string"},
            },
        },
    },
}


def validate_config(config: dict) -> None:
    """Raise jsonschema.ValidationError if config is invalid."""
    jsonschema.validate(config, CONFIG_SCHEMA)
