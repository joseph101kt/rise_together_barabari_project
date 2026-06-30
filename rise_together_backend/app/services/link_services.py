"""
LinkService

Responsible for fetching and parsing Open Graph metadata from URLs.

This service is intentionally independent from repositories so it can be
reused anywhere links are created or updated.

Usage:

    metadata = LinkService.fetch_metadata("https://github.com/joseph101kt")

Returns:

{
    "og_title": "...",
    "og_description": "...",
    "og_image": "...",
    "fetched_at": datetime.utcnow(),
}

If fetching fails, all metadata fields are None except fetched_at.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TypedDict

import requests
from bs4 import BeautifulSoup


class LinkMetadata(TypedDict):
    og_title: str | None
    og_description: str | None
    og_image: str | None
    fetched_at: datetime


class LinkService:
    DEFAULT_TIMEOUT = 10

    DEFAULT_HEADERS = {
        "User-Agent": (
            "RiseTogetherBot/1.0 "
            "(https://rise-together.app)"
        )
    }

    @classmethod
    def fetch_metadata(cls, url: str) -> LinkMetadata:
        """
        Downloads a webpage and extracts Open Graph metadata.

        Falls back to HTML <title> and meta description when OG tags
        are unavailable.

        Never raises an exception.
        """

        try:
            response = requests.get(
                url,
                headers=cls.DEFAULT_HEADERS,
                timeout=cls.DEFAULT_TIMEOUT,
                allow_redirects=True,
            )

            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            title = cls._extract(
                soup,
                "og:title",
                fallback_title=True,
            )

            description = cls._extract(
                soup,
                "og:description",
                fallback_description=True,
            )

            image = cls._extract(
                soup,
                "og:image",
            )

            return {
                "og_title": title,
                "og_description": description,
                "og_image": image,
                "fetched_at": datetime.now(timezone.utc),
            }

        except Exception:
            return {
                "og_title": None,
                "og_description": None,
                "og_image": None,
                "fetched_at": datetime.now(timezone.utc),
            }

    @staticmethod
    def _extract(
        soup: BeautifulSoup,
        property_name: str,
        *,
        fallback_title: bool = False,
        fallback_description: bool = False,
    ) -> str | None:
        """
        Extract an Open Graph property.

        Falls back to standard HTML tags when requested.
        """

        tag = soup.find(
            "meta",
            attrs={"property": property_name},
        )

        if tag and tag.get("content"):
            return tag["content"].strip()

        tag = soup.find(
            "meta",
            attrs={"name": property_name},
        )

        if tag and tag.get("content"):
            return tag["content"].strip()

        if fallback_title:
            if soup.title and soup.title.string:
                return soup.title.string.strip()

        if fallback_description:
            tag = soup.find(
                "meta",
                attrs={"name": "description"},
            )

            if tag and tag.get("content"):
                return tag["content"].strip()

        return None