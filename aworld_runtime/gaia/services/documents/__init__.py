"""The `documents` service provides a collection of tools for extracting content and metadata from various document types.

This service includes collections for handling:
- CSV files (`CSVCollection`)
- DOCX files (`DOCXExtractionCollection`)
- PDF documents (`PDFDocumentCollection`)
- PPTX presentations (`PPTXCollection`)
- Plain text files (`TextCollection`)
- XLSX spreadsheets (`XLSXCollection`)

The `DocumentMetadata` model is a shared Pydantic model used for storing common document metadata.
"""

from ...models.document import DocumentMetadata
from .csv_collection import CSVCollection
from .docx_collection import DOCXExtractionCollection
from .pdf_collection import PDFDocumentCollection
from .pptx_collection import PPTXCollection
from .txt_collection import TextCollection
from .xlsx_collection import XLSXCollection

__all__ = [
    "CSVCollection",
    "DOCXExtractionCollection",
    "PDFDocumentCollection",
    "PPTXCollection",
    "TextCollection",
    "XLSXCollection",
    "DocumentMetadata",
]
