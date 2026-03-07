from flask import jsonify

class AppError(Exception):
    http_status = 500
    error_code  = "INTERNAL_ERROR"
    def __init__(self, message, details=None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    def to_response(self):
        body = {"status":"error","error_code":self.error_code,"message":self.message}
        if self.details: body["details"] = self.details
        return jsonify(body), self.http_status

class MissingFileError(AppError):
    http_status=400; error_code="MISSING_FILE"
    def __init__(self): super().__init__("No file provided. Attach a file to the request.")

class EmptyFilenameError(AppError):
    http_status=400; error_code="EMPTY_FILENAME"
    def __init__(self): super().__init__("Uploaded file has no filename.")

class UnsupportedFileTypeError(AppError):
    http_status=400; error_code="UNSUPPORTED_FILE_TYPE"
    def __init__(self,fn): super().__init__(f"Unsupported file: '{fn}'. Use .xlsx/.xls/.csv",{"filename":fn,"accepted":[".xlsx",".xls",".csv"]})

class EmptyFileError(AppError):
    http_status=400; error_code="EMPTY_FILE"
    def __init__(self): super().__init__("File is empty or has no data rows.")

class MissingColumnError(AppError):
    http_status=400; error_code="MISSING_COLUMN"
    def __init__(self,missing,found): super().__init__(f"Required columns not found: {missing}",{"missing":missing,"found":found})

class InvalidAmountError(AppError):
    http_status=400; error_code="INVALID_AMOUNT"
    def __init__(self,v): super().__init__(f"'{v}' is not a valid number.",{"value":str(v)})

class ClientNotFoundError(AppError):
    http_status=404; error_code="CLIENT_NOT_FOUND"
    def __init__(self,c,avail): super().__init__(f"Client '{c}' not found.",{"requested":c,"available":avail})

class NoNumericDataError(AppError):
    http_status=422; error_code="NO_NUMERIC_DATA"
    def __init__(self): super().__init__("No valid PRIX/QTÉ numeric data found in file.")

class PDFGenerationError(AppError):
    http_status=500; error_code="PDF_GENERATION_FAILED"
    def __init__(self,r): super().__init__(f"PDF generation failed: {r}",{"reason":r})

class DataFileNotFoundError(AppError):
    http_status=500; error_code="DATA_FILE_NOT_FOUND"
    def __init__(self,p): super().__init__(f"Server data file missing: {p}",{"path":p})

class CounterError(AppError):
    http_status=500; error_code="COUNTER_ERROR"
    def __init__(self,r): super().__init__(f"Invoice counter error: {r}",{"reason":r})