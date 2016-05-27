import json

from sys import version_info
import yaml
from cerberus import Validator


PYTHON_MAJOR_VERSION = version_info[0]

try:  # First try to load pyresttest from global namespace
    from pyresttest import validators
    from pyresttest import binding
    from pyresttest import parsing
    from pyresttest import contenthandling
except ImportError:  # Then try a relative import if possible
    from .. import validators
    from .. import binding
    from .. import parsing
    from .. import contenthandling


class JsonSchemaValidator(validators.AbstractValidator):
    """ Json schema validator using the cerberus library """
    schema = None

    def validate(self, body=None, headers=None, context=None):
        schema_text = self.schema.get_content(context=context)
        schema = yaml.safe_load(schema_text)
        parsed_body = body
        if PYTHON_MAJOR_VERSION > 2 and isinstance(body, bytes):
            parsed_body = str(body, 'utf-8')
        v = Validator()
        if v.validate(json.loads(parsed_body), schema):
            return True
        trace = v.errors
        return validators.Failure(message="JSON Schema Validation Failed", details=trace, validator=self, failure_type=validators.FAILURE_VALIDATOR_EXCEPTION)

    def get_readable_config(self, context=None):
        return "JSON schema validation"

    @classmethod
    def parse(cls, config):
        validator = JsonSchemaValidator()
        config = parsing.lowercase_keys(config)
        if 'schema' not in config:
            raise ValueError(
                "Cannot create schema validator without a 'schema' configuration element!")
        validator.schema = contenthandling.ContentHandler.parse_content(config[
                                                                        'schema'])
        return validator

VALIDATORS = {'SchemaValidation': JsonSchemaValidator.parse}
