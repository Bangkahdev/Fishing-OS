import unittest

from fishing_agent.policy import Risk
from fishing_agent.registry import (
    StepOutcome,
    ToolContext,
    ToolError,
    ToolNotFound,
    ToolRegistry,
    ToolSpec,
    ToolValidationError,
    validate_arguments,
)


class SchemaValidationTest(unittest.TestCase):
    def test_required_dan_tipe(self):
        schema = {
            "type": "object",
            "properties": {"command": {"type": "string", "minLength": 1}, "args": {"type": "array", "items": {"type": "string"}}},
            "required": ["command"],
            "additionalProperties": False,
        }
        self.assertEqual(validate_arguments(schema, {"command": "ls"}), {"command": "ls"})
        with self.assertRaises(ToolValidationError):
            validate_arguments(schema, {})  # required hilang
        with self.assertRaises(ToolValidationError):
            validate_arguments(schema, {"command": ""})  # minLength
        with self.assertRaises(ToolValidationError):
            validate_arguments(schema, {"command": 123})  # tipe salah
        with self.assertRaises(ToolValidationError):
            validate_arguments(schema, {"command": "ls", "unknown": 1})  # additionalProperties false

    def test_enum_default_dan_numerik(self):
        schema = {
            "type": "object",
            "properties": {
                "mode": {"type": "string", "enum": ["argv", "shell"], "default": "argv"},
                "timeout": {"type": "number", "minimum": 0.1, "default": 60.0},
            },
        }
        result = validate_arguments(schema, {})
        self.assertEqual(result, {"mode": "argv", "timeout": 60.0})
        with self.assertRaises(ToolValidationError):
            validate_arguments(schema, {"mode": "invalid"})
        with self.assertRaises(ToolValidationError):
            validate_arguments(schema, {"timeout": 0})

    def test_min_items_dan_max_items(self):
        schema = {"type": "object", "properties": {"slides": {"type": "array", "minItems": 1, "maxItems": 2, "items": {"type": "string"}}}}
        self.assertEqual(validate_arguments(schema, {"slides": ["a"]}), {"slides": ["a"]})
        with self.assertRaises(ToolValidationError):
            validate_arguments(schema, {"slides": []})
        with self.assertRaises(ToolValidationError):
            validate_arguments(schema, {"slides": ["a", "b", "c"]})
        with self.assertRaises(ToolValidationError):
            validate_arguments(schema, {"slides": [1]})


class RegistryTest(unittest.TestCase):
    def _context(self):
        return ToolContext(policy=object(), administrator=object(), stop=object())

    def test_register_dan_dispatch(self):
        registry = ToolRegistry()

        def handler(arguments, context):
            return StepOutcome(ok=True, summary=f"echo {arguments['message']}")

        registry.register(
            ToolSpec(
                name="echo",
                description="uji",
                parameters={"type": "object", "properties": {"message": {"type": "string"}}, "required": ["message"], "additionalProperties": False},
                handler=handler,
                risk=Risk.LOW,
            )
        )
        outcome = registry.dispatch("echo", {"message": "halo"}, self._context())
        self.assertTrue(outcome.ok)
        self.assertIn("halo", outcome.summary)

    def test_dispatch_menolak_argumen_invalid_sebelum_handler(self):
        called = {"count": 0}

        def handler(arguments, context):  # pragma: no cover - tidak boleh terpanggil
            called["count"] += 1
            return StepOutcome(ok=True)

        registry = ToolRegistry()
        registry.register(
            ToolSpec(
                name="echo",
                description="uji",
                parameters={"type": "object", "properties": {"message": {"type": "string"}}, "required": ["message"]},
                handler=handler,
            )
        )
        with self.assertRaises(ToolValidationError):
            registry.dispatch("echo", {}, self._context())
        self.assertEqual(called["count"], 0)

    def test_unknown_tool(self):
        with self.assertRaises(ToolNotFound):
            ToolRegistry().dispatch("missing", {}, self._context())

    def test_spec_menolak_schema_tidak_valid(self):
        with self.assertRaises(ToolValidationError):
            ToolSpec(name="x", description="", parameters={"type": "object", "properties": {"a": {"type": "unknown"}}})
        with self.assertRaises(ToolValidationError):
            ToolSpec(name="x", description="", parameters={"type": "object", "properties": {"a": {"type": "string"}}, "required": ["b"]})

    def test_schemas_render(self):
        registry = ToolRegistry()
        registry.register(
            ToolSpec(
                name="echo",
                description="uji",
                parameters={"type": "object", "properties": {"message": {"type": "string"}}},
                handler=lambda a, c: StepOutcome(ok=True),
                examples=("echo halo",),
            )
        )
        rendered = registry.schemas()
        self.assertEqual(rendered[0]["name"], "echo")
        self.assertIn("examples", rendered[0])


if __name__ == "__main__":
    unittest.main()