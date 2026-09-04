"""Shelf proximity logic for Person 3."""

from __future__ import annotations

from kyra.contracts import PersonTrack, ShelfConfig


def is_person_near_shelf(
    track: PersonTrack,
    shelf: ShelfConfig,
) -> bool:
    """Return whether a tracked person is within the configured shelf distance."""

    if track.position_m is None:
        return False

    x, y, z = track.position_m

    min_x, min_y, min_z = shelf.bounds_min_m
    max_x, max_y, max_z = shelf.bounds_max_m

    # Distance from the person's 3D position to the shelf bounding box.
    dx = max(min_x - x, 0.0, x - max_x)
    dy = max(min_y - y, 0.0, y - max_y)
    dz = max(min_z - z, 0.0, z - max_z)

    distance_m = (dx * dx + dy * dy + dz * dz) ** 0.5

    return distance_m <= shelf.proximity_distance_m


def update_proximity(
    track: PersonTrack,
    shelf: ShelfConfig,
) -> PersonTrack:
    """Update a PersonTrack with deterministic shelf-proximity state."""

    track.near_shelf = is_person_near_shelf(track, shelf)

    if track.near_shelf:
        track.last_near_timestamp_ns = track.timestamp_ns

    return track
