"""Query parameter models for OpenGov API."""

from datetime import date, datetime, timedelta, timezone
from typing import Any
from pydantic import BaseModel, Field

from .enums import RecordStatus


class DateRangeFilter(BaseModel):
    """
    Date range filter with comparison operators.

    Example:
        >>> from datetime import date
        >>> # Records created after March 1, 2025
        >>> filter_created_at = DateRangeFilter(gt=date(2025, 3, 1))
        >>>
        >>> # Records created in Q1 2025
        >>> filter_created_at = DateRangeFilter(
        ...     gte=date(2025, 1, 1),
        ...     lt=date(2025, 4, 1)
        ... )
        >>>
        >>> # Records from the last 30 days
        >>> filter_created_at = DateRangeFilter.last_days(30)
        >>>
        >>> # Records older than 90 days
        >>> filter_created_at = DateRangeFilter.older_than_days(90)
    """

    gt: date | datetime | None = None  # greater than
    gte: date | datetime | None = None  # greater than or equal
    lt: date | datetime | None = None  # less than
    lte: date | datetime | None = None  # less than or equal

    @classmethod
    def last_days(cls, days: int) -> "DateRangeFilter":
        """
        Create a filter for records from the last N days.

        Args:
            days: Number of days to look back from now

        Returns:
            DateRangeFilter configured for the last N days

        Example:
            >>> # Records from the last 30 days
            >>> filter_created_at = DateRangeFilter.last_days(30)
        """
        now = datetime.now(timezone.utc)
        start = now - timedelta(days=days)
        return cls(gte=start)

    @classmethod
    def older_than_days(cls, days: int) -> "DateRangeFilter":
        """
        Create a filter for records older than N days.

        Args:
            days: Number of days ago to use as threshold

        Returns:
            DateRangeFilter configured for records older than N days

        Example:
            >>> # Records older than 90 days
            >>> filter_created_at = DateRangeFilter.older_than_days(90)
        """
        now = datetime.now(timezone.utc)
        threshold = now - timedelta(days=days)
        return cls(lt=threshold)

    @classmethod
    def between_days(cls, start_days_ago: int, end_days_ago: int = 0) -> "DateRangeFilter":
        """
        Create a filter for records between N days ago and M days ago.

        Args:
            start_days_ago: Number of days ago for the start of the range
            end_days_ago: Number of days ago for the end of the range (default: 0 = now)

        Returns:
            DateRangeFilter configured for the specified date range

        Example:
            >>> # Records between 60 and 30 days ago
            >>> filter_created_at = DateRangeFilter.between_days(60, 30)
            >>>
            >>> # Records between 7 days ago and now
            >>> filter_created_at = DateRangeFilter.between_days(7)
        """
        now = datetime.now(timezone.utc)
        start = now - timedelta(days=start_days_ago)
        end = now - timedelta(days=end_days_ago)
        return cls(gte=start, lte=end)

    def to_query_params(self, field_name: str) -> dict[str, str]:
        """
        Convert to query parameter dict with nested bracket notation.

        Args:
            field_name: The field name (e.g., "createdAt")

        Returns:
            Dictionary with keys like "filter[createdAt][gt]"
        """
        params = {}
        if self.gt:
            params[f"filter[{field_name}][gt]"] = self._format_date(self.gt)
        if self.gte:
            params[f"filter[{field_name}][gte]"] = self._format_date(self.gte)
        if self.lt:
            params[f"filter[{field_name}][lt]"] = self._format_date(self.lt)
        if self.lte:
            params[f"filter[{field_name}][lte]"] = self._format_date(self.lte)
        return params

    @staticmethod
    def _format_date(value: date | datetime) -> str:
        """Format date/datetime to ISO string."""
        if isinstance(value, datetime):
            return value.isoformat()
        return value.isoformat()


class PageParams(BaseModel):
    """Pagination parameters."""

    number: int = Field(1, alias="page[number]", ge=1)
    size: int = Field(20, alias="page[size]", ge=1, le=100)

    model_config = {"populate_by_name": True}


class ListRecordsParams(BaseModel):
    """
    Query parameters for listing records.

    Example:
        >>> from opengov_api.models import ListRecordsParams, RecordStatus, DateRangeFilter
        >>> from datetime import date
        >>>
        >>> # Simple filter
        >>> params = ListRecordsParams(
        ...     filter_status=RecordStatus.ACTIVE,
        ...     filter_is_enabled=True
        ... )
        >>>
        >>> # Date range filter
        >>> params = ListRecordsParams(
        ...     filter_created_at=DateRangeFilter(gt=date(2025, 3, 1)),
        ...     page_size=50
        ... )
    """

    # Filters
    filter_number: str | None = None
    filter_hist_id: str | None = None
    filter_hist_number: str | None = None
    filter_type_id: str | None = None
    filter_project_id: str | None = None
    filter_status: RecordStatus | None = None
    filter_created_at: date | datetime | DateRangeFilter | None = None
    filter_updated_at: date | datetime | DateRangeFilter | None = None
    filter_submitted_at: date | datetime | DateRangeFilter | None = None
    filter_expires_at: date | datetime | DateRangeFilter | None = None
    filter_is_enabled: bool | None = None
    filter_renewal_submitted: bool | None = None
    filter_submitted_online: bool | None = None
    filter_renewal_number: str | None = None
    filter_renewal_of_record_id: str | None = None

    # Pagination
    page_number: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)

    # JSON:API standard params
    include: list[str] | None = None
    fields: dict[str, list[str]] | None = None
    sort: str | None = None

    def to_query_params(self) -> dict[str, Any]:
        """
        Convert to query parameter dict with proper JSON:API bracket notation.

        Returns:
            Dictionary suitable for httpx params argument
        """
        params: dict[str, Any] = {}

        # Simple filters
        if self.filter_number:
            params["filter[number]"] = self.filter_number
        if self.filter_hist_id:
            params["filter[histID]"] = self.filter_hist_id
        if self.filter_hist_number:
            params["filter[histNumber]"] = self.filter_hist_number
        if self.filter_type_id:
            params["filter[typeID]"] = self.filter_type_id
        if self.filter_project_id:
            params["filter[projectID]"] = self.filter_project_id
        if self.filter_status:
            params["filter[status]"] = self.filter_status.value
        if self.filter_is_enabled is not None:
            params["filter[isEnabled]"] = self.filter_is_enabled
        if self.filter_renewal_submitted is not None:
            params["filter[renewalSubmitted]"] = self.filter_renewal_submitted
        if self.filter_submitted_online is not None:
            params["filter[submittedOnline]"] = self.filter_submitted_online
        if self.filter_renewal_number:
            params["filter[renewalNumber]"] = self.filter_renewal_number
        if self.filter_renewal_of_record_id:
            params["filter[renewalOfRecordID]"] = self.filter_renewal_of_record_id

        # Date filters (can be simple date or range)
        for field_name, param_value in [
            ("createdAt", self.filter_created_at),
            ("updatedAt", self.filter_updated_at),
            ("submittedAt", self.filter_submitted_at),
            ("expiresAt", self.filter_expires_at),
        ]:
            if param_value:
                if isinstance(param_value, DateRangeFilter):
                    params.update(param_value.to_query_params(field_name))
                else:
                    # Simple date/datetime
                    params[f"filter[{field_name}]"] = (
                        param_value.isoformat()
                        if isinstance(param_value, (date, datetime))
                        else param_value
                    )

        # Pagination
        params["page[number]"] = self.page_number
        params["page[size]"] = self.page_size

        # JSON:API standard params
        if self.include:
            params["include"] = ",".join(self.include)
        if self.fields:
            for resource_type, field_list in self.fields.items():
                params[f"fields[{resource_type}]"] = ",".join(field_list)
        if self.sort:
            params["sort"] = self.sort

        return params
