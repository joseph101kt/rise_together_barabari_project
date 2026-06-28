"""
LinkMetadataService

Responsible for fetching metadata from a URL.

Priority:
1. OpenGraph tags
2. Twitter Card tags
3. HTML <title>
4. Meta description

This service NEVER raises exceptions.
If fetching fails, it simply returns empty metadata.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup


@dataclass(slots=True)
class LinkMetadata:
    title: str | None = None
    description: str | None = None
    image: str | None = None
    fetched_at: datetime | None = None


class LinkMetadataService:
    """
    Fetches OpenGraph metadata from webpages.

    Usage
    -----
    metadata = LinkMetadataService().fetch("https://github.com")

    metadata.title
    metadata.description
    metadata.image
    """

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0 Safari/537.36"
    )

    TIMEOUT = 5.0

    def fetch(self, url: str) -> LinkMetadata:
        """
        Fetch metadata for a URL.

        Never raises exceptions.
        """
        try:
            with httpx.Client(
                follow_redirects=True,
                timeout=self.TIMEOUT,
                headers={"User-Agent": self.USER_AGENT},
            ) as client:
                response = client.get(url)

            if response.status_code >= 400:
                return LinkMetadata()

            soup = BeautifulSoup(response.text, "html.parser")

            title = (
                self._meta_property(soup, "og:title")
                or self._meta_name(soup, "twitter:title")
                or self._title(soup)
            )

            description = (
                self._meta_property(soup, "og:description")
                or self._meta_name(soup, "twitter:description")
                or self._meta_name(soup, "description")
            )

            image = (
                self._meta_property(soup, "og:image")
                or self._meta_name(soup, "twitter:image")
            )

            if image:
                image = urljoin(str(response.url), image)

            return LinkMetadata(
                title=title,
                description=description,
                image=image,
                fetched_at=datetime.utcnow(),
            )

        except Exception:
            return LinkMetadata()

    @staticmethod
    def _meta_property(
        soup: BeautifulSoup,
        prop: str,
    ) -> str | None:
        tag = soup.find("meta", property=prop)

        if tag is None:
            return None

        value = tag.get("content")

        if value:
            value = value.strip()

        return value or None

    @staticmethod
    def _meta_name(
        soup: BeautifulSoup,
        name: str,
    ) -> str | None:
        tag = soup.find("meta", attrs={"name": name})

        if tag is None:
            return None

        value = tag.get("content")

        if value:
            value = value.strip()

        return value or None

    @staticmethod
    def _title(
        soup: BeautifulSoup,
    ) -> str | None:
        if soup.title is None:
            return None

        if soup.title.string is None:
            return None

        value = soup.title.string.strip()

        return value or None