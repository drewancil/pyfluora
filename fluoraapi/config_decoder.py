"""Class to decode Fluora binary config dumps using legacy schema & OSC routes."""

from __future__ import annotations

import json
import re
import struct
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple


@dataclass(frozen=True)
class RouteInfo:
    """Information about a specific OSC route from the schema."""

    route: str
    type: Optional[str]
    label: Optional[str]
    path: str


class FluoraConfigDecoder:
    """
    Decode Fluora binary using legacy schema & OSC routes.

    IMPORTANT: In this format, the value typically PRECEDES the route.

    Result is a nested dict mirroring schema paths with:
      { "route": str, "type": str|None, "label": str|None, "value": Any|None }
    """

    ROUTE_PAT = re.compile(rb"/[A-Za-z0-9_\-]{10,24}")

    def __init__(
        self,
        schema: Dict[str, Any],
        *,
        float_hint_range: Tuple[float, float] = (-0.1, 1.1),
        back_window: int = 32,
        scan_words: int = 4,
    ) -> None:
        self.schema = schema
        self.float_hint_range = float_hint_range
        self.back_window = back_window
        self.scan_words = scan_words

        self._route_map: Dict[str, RouteInfo] = {}
        self._build_route_map(schema)

    def decode(self, bin_bytes: bytes) -> Dict[str, Any]:
        """Decode binary data into nested dict using schema routes."""
        results = []

        for m in self.ROUTE_PAT.finditer(bin_bytes):
            route = m.group().decode("ascii")
            info = self._route_map.get(route)
            if not info:
                continue

            val: Any = None
            if info.type in ("float", "int", "boolean"):
                val = self._find_value_before(bin_bytes, m.start(), info.type)

            results.append(
                (
                    info.path,
                    {
                        "route": route,
                        "type": info.type,
                        "label": info.label,
                        "value": val,
                    },
                )
            )

        # Rebuild nested dict by schema path
        root: Dict[str, Any] = {}
        for path, payload in results:
            self._set_path(root, path, payload)
        return root

    # Internal: schema processing
    def _build_route_map(self, schema: Dict[str, Any]) -> None:
        def walk(obj: Any, path: str = "") -> None:
            if isinstance(obj, dict):
                if "route" in obj and "type" in obj:
                    route = obj.get("route")
                    rtype = obj.get("type")
                    label = obj.get("label") or (path.split("/")[-1] if path else None)
                    if route:
                        self._route_map[route] = RouteInfo(route, rtype, label, path)
                for k, v in obj.items():
                    sub = f"{path}/{k}" if path else k
                    walk(v, sub)
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    sub = f"{path}[{i}]"
                    walk(v, sub)

        walk(schema)

    # Internal: decode helpers
    def _find_value_before(self, blob: bytes, route_start: int, vtype: str) -> Any:
        # Canonical pattern: [value][u32 route_len][/route...]
        len_off = route_start - 4
        if len_off >= 0:
            route_len = self._u32_le(blob, len_off)
            if route_len and 4 <= route_len <= 48:
                val_off = len_off - 4
                if vtype == "float":
                    v = self._f32_le(blob, val_off)
                    if v is not None and self._float_in_range(v):
                        return v
                elif vtype == "int":
                    v = self._i32_le(blob, val_off)
                    if v is not None:
                        return v
                elif vtype == "boolean":
                    v = self._b32_le(blob, val_off)
                    if v is not None:
                        return v

        # Fallback: scan a small backward region, aligned 4B candidates nearest first
        for step in range(0, self.scan_words * 4, 4):
            off = (route_start - 4) - step
            if vtype == "float":
                v = self._f32_le(blob, off)
                if v is not None and self._float_in_range(v):
                    return v
            elif vtype == "int":
                v = self._i32_le(blob, off)
                if v is not None:
                    return v
            elif vtype == "boolean":
                v = self._b32_le(blob, off)
                if v is not None:
                    return v

        # As a last resort for bool, try 1 byte before route_len (u8)
        if vtype == "boolean":
            u8_off = route_start - 5
            if 0 <= u8_off < len(blob):
                return blob[u8_off] == 1

        return None

    # Internal: path utilities
    @staticmethod
    def _set_path(d: Dict[str, Any], path: str, payload: Any) -> None:
        parts = [p for p in path.split("/") if p]
        if not parts:
            return
        cur = d
        for p in parts[:-1]:
            cur = cur.setdefault(p, {})
        cur[parts[-1]] = payload

    # Internal: binary readers
    @staticmethod
    def _f32_le(blob: bytes, off: int) -> Optional[float]:
        if off < 0 or off + 4 > len(blob):
            return None
        return struct.unpack_from("<f", blob, off)[0]

    @staticmethod
    def _i32_le(blob: bytes, off: int) -> Optional[int]:
        if off < 0 or off + 4 > len(blob):
            return None
        return struct.unpack_from("<i", blob, off)[0]

    @staticmethod
    def _u32_le(blob: bytes, off: int) -> Optional[int]:
        if off < 0 or off + 4 > len(blob):
            return None
        return struct.unpack_from("<I", blob, off)[0]

    @staticmethod
    def _b32_le(blob: bytes, off: int) -> Optional[bool]:
        v = FluoraConfigDecoder._u32_le(blob, off)
        return (v == 1) if v in (0, 1) else None

    # Internal: predicates
    def _float_in_range(self, v: float) -> bool:
        lo, hi = self.float_hint_range
        return lo <= v <= hi


# example usage
if __name__ == "__main__":
    with open("Fluora-Config.txt", encoding="utf-8") as f:
        my_schema = json.load(f)
        decoder = FluoraConfigDecoder(my_schema)

        with open("bytes.txt", "rb") as f:
            byte_blob = f.read()
            reconstructed = decoder.decode(byte_blob)
            print(json.dumps(reconstructed, indent=2))
