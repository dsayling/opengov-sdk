"""HTTP cache helper utilities for OpenGov API SDK."""

import datetime
from email.utils import parsedate_to_datetime
from typing import Any

import httpx


class HTTPCacheHelper:
    """Helper for handling HTTP cache headers."""

    @staticmethod
    def parse_cache_control(cache_control: str | None) -> dict[str, str | None]:
        """
        Parse Cache-Control header.

        Args:
            cache_control: Cache-Control header value

        Returns:
            Dictionary of cache directives
        """
        if not cache_control:
            return {}

        directives = {}
        for directive in cache_control.split(","):
            directive = directive.strip()  # noqa: PLW2901
            if "=" in directive:
                key, value = directive.split("=", 1)
                directives[key.strip().lower()] = value.strip().strip('"')
            else:
                directives[directive.lower()] = None

        return directives

    @staticmethod
    def is_cacheable(response: httpx.Response) -> bool:
        """
        Determine if response is cacheable.

        Args:
            response: HTTP response

        Returns:
            True if response can be cached
        """
        # Don't cache error responses
        if response.status_code >= httpx.codes.BAD_REQUEST:
            return False

        cache_control = HTTPCacheHelper.parse_cache_control(
            response.headers.get("Cache-Control")
        )

        # Don't cache if explicitly forbidden
        if "no-cache" in cache_control or "no-store" in cache_control:
            return False

        # Cache GET requests by default
        return True

    @staticmethod
    def get_cache_ttl(response: httpx.Response) -> int | None:
        """
        Get cache TTL from response headers.

        Args:
            response: HTTP response

        Returns:
            TTL in seconds, None if not specified
        """
        cache_control = HTTPCacheHelper.parse_cache_control(
            response.headers.get("Cache-Control")
        )

        # Check for max-age directive
        max_age = cache_control.get("max-age")
        if max_age:
            try:
                return int(max_age)
            except ValueError:
                pass

        # Check for Expires header
        expires = response.headers.get("Expires")
        if expires:
            try:
                expires_dt = parsedate_to_datetime(expires)
                now = datetime.datetime.now(datetime.UTC)
                ttl = int((expires_dt - now).total_seconds())
                return max(0, ttl)
            except Exception:
                pass

        return None

    @staticmethod
    def should_revalidate(
        cached_response: dict[str, Any], request_headers: dict[str, str] | None = None
    ) -> bool:
        """
        Determine if cached response should be revalidated.

        Args:
            cached_response: Cached response data
            request_headers: Request headers

        Returns:
            True if should revalidate with server
        """
        # Check for ETag or Last-Modified in cached response
        response_headers = cached_response.get("headers", {})
        etag = response_headers.get("ETag")
        last_modified = response_headers.get("Last-Modified")

        # If we have conditional headers, we can revalidate
        return bool(etag or last_modified)

    @staticmethod
    def add_conditional_headers(
        headers: dict[str, str], cached_response: dict[str, Any]
    ) -> dict[str, str]:
        """
        Add conditional headers for cache revalidation.

        Args:
            headers: Request headers to modify
            cached_response: Cached response data

        Returns:
            Updated headers with conditional headers
        """
        headers = headers.copy()
        response_headers = cached_response.get("headers", {})

        # Add If-None-Match (ETag)
        etag = response_headers.get("ETag")
        if etag:
            headers["If-None-Match"] = etag

        # Add If-Modified-Since (Last-Modified)
        last_modified = response_headers.get("Last-Modified")
        if last_modified:
            headers["If-Modified-Since"] = last_modified

        return headers
