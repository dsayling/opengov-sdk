"""Base JSON:API models for OpenGov API responses."""

from typing import Any, Generic, TypeVar
from pydantic import BaseModel, Field


class Links(BaseModel):
    """JSON:API Links object."""

    self: str | None = None
    related: str | None = None
    first: str | None = None
    prev: str | None = None
    next: str | None = None
    last: str | None = None


class Meta(BaseModel):
    """JSON:API Meta object for pagination."""

    page: int | None = None
    size: int | None = None
    total_pages: int | None = Field(None, alias="totalPages")
    total_records: int | None = Field(None, alias="totalRecords")

    model_config = {"populate_by_name": True}


class RelationshipData(BaseModel):
    """JSON:API Relationship data object."""

    id: str
    type: str


class Relationship(BaseModel):
    """JSON:API Relationship object."""

    data: RelationshipData | list[RelationshipData] | None = None
    links: Links | None = None


T = TypeVar("T")


class ResourceObject(BaseModel, Generic[T]):
    """JSON:API Resource Object."""

    id: str
    type: str
    attributes: T
    relationships: dict[str, Relationship] | None = None
    links: Links | None = None


class JSONAPIResponse(BaseModel, Generic[T]):
    """
    JSON:API Response wrapper with pagination support.

    Example:
        >>> response = list_records(page_size=10)
        >>> for record in response.data:
        ...     print(record.attributes.name)
        >>>
        >>> # Check pagination
        >>> if response.has_next_page():
        ...     print(f"Page {response.current_page()} of {response.total_pages()}")
        >>>
        >>> # Or iterate all pages automatically
        >>> for record in iter_records():
        ...     print(record.attributes.name)
    """

    data: T | list[T]
    included: list[dict[str, Any]] | None = None
    links: Links | None = None
    meta: Meta | None = None

    def has_next_page(self) -> bool:
        """Check if there is a next page available."""
        return self.links is not None and self.links.next is not None

    def has_prev_page(self) -> bool:
        """Check if there is a previous page available."""
        return self.links is not None and self.links.prev is not None

    def current_page(self) -> int | None:
        """Get the current page number."""
        return self.meta.page if self.meta else None

    def page_size(self) -> int | None:
        """Get the page size."""
        return self.meta.size if self.meta else None

    def total_pages(self) -> int | None:
        """Get the total number of pages."""
        return self.meta.total_pages if self.meta else None

    def total_records(self) -> int | None:
        """Get the total number of records across all pages."""
        return self.meta.total_records if self.meta else None

    def next_page_url(self) -> str | None:
        """Get the URL for the next page."""
        return self.links.next if self.links else None

    def prev_page_url(self) -> str | None:
        """Get the URL for the previous page."""
        return self.links.prev if self.links else None
