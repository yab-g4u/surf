from __future__ import annotations

import hashlib

from core.schema import Document


def compute_content_hash(document: Document) -> str:
    canonical = "|".join(
        [
            document.title or "",
            document.body,
            document.author or "",
            ",".join(sorted(document.tags)),
            str(sorted(document.metadata.items())),
        ]
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
