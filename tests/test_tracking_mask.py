from kyra.contracts import PersonTrack
from kyra.proximity.occlusion import build_person_occlusion_mask


def make_track(
    *,
    box_xyxy=(2.0, 3.0, 6.0, 7.0),
) -> PersonTrack:
    return PersonTrack(
        track_id=7,
        timestamp_ns=1_000_000_000,
        box_xyxy=box_xyxy,
        pose_keypoints_xyc=[
            (3.0, 4.0, 0.9),
            (5.0, 6.0, 0.8),
        ],
        position_m=(0.1, 0.0, 0.8),
        near_shelf=True,
        authorized=False,
        last_near_timestamp_ns=1_000_000_000,
    )


def test_person_bbox_is_marked_in_occlusion_mask():
    track = make_track()

    mask = build_person_occlusion_mask(
        tracks=(track,),
        frame_shape=(10, 10),
    )

    assert mask.shape == (10, 10)
    assert mask.dtype == bool

    # Inside the person's bounding box.
    assert mask[4, 3]
    assert mask[6, 5]


def test_background_outside_person_is_not_occluded():
    track = make_track()

    mask = build_person_occlusion_mask(
        tracks=(track,),
        frame_shape=(10, 10),
    )

    assert not mask[0, 0]
    assert not mask[9, 9]


def test_multiple_people_are_combined():
    first = make_track(box_xyxy=(1.0, 1.0, 3.0, 3.0))
    second = make_track(box_xyxy=(6.0, 6.0, 8.0, 8.0))

    mask = build_person_occlusion_mask(
        tracks=(first, second),
        frame_shape=(10, 10),
    )

    assert mask[2, 2]
    assert mask[7, 7]
    assert not mask[5, 5]


def test_empty_tracks_produce_empty_mask():
    mask = build_person_occlusion_mask(
        tracks=(),
        frame_shape=(10, 10),
    )

    assert mask.shape == (10, 10)
    assert not mask.any()


def test_bbox_is_clipped_to_frame():
    track = make_track(box_xyxy=(-5.0, -5.0, 15.0, 15.0))

    mask = build_person_occlusion_mask(
        tracks=(track,),
        frame_shape=(10, 10),
    )

    assert mask.all()
