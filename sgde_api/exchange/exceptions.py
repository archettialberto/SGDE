from sgde_api.exceptions import NotFound, BadRequest


class GeneratorNotFound(NotFound):
    DETAIL = "Generator not found"


class GeneratorExists(BadRequest):
    DETAIL = "Generator already exists"


class InvalidONNXError(BadRequest):
    DETAIL = "Invalid ONNX file"


class FileWritingError(BadRequest):
    DETAIL = "The file could not be saved"


class InvalidJSONError(BadRequest):
    DETAIL = "Invalid JSON file"
