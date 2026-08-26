from __future__ import annotations

import numpy as np

from kyra.contracts import FramePacket, SourceType


def make_frame_packet() -> FramePacket:
    depth_m = np.array(
        [[1.25, 0.0, np.nan], [2.5, -0.5, np.inf]],
        dtype=np.float64,
    )
    return FramePacket(
        frame_id="compatibility-frame-0001",
        timestamp_ns=1_234_567_890,
        rgb=np.zeros((2, 3, 3), dtype=np.int16),
        depth_m=depth_m,
        valid_depth_mask=np.array(
            [[True, True, True], [True, False, True]],
            dtype=np.uint8,
        ),
        intrinsics=np.array(
            [[600.0, 0.0, 1.0], [0.0, 601.0, 0.5], [0.0, 0.0, 1.0]],
            dtype=np.float32,
        ),
        camera_to_shelf=np.array(
            [
                [1.0, 0.0, 0.0, 0.1],
                [0.0, 1.0, 0.0, 0.2],
                [0.0, 0.0, 1.0, 0.3],
                [0.0, 0.0, 0.0, 1.0],
            ],
            dtype=np.float32,
        ),
        source_type=SourceType.SYNTHETIC_RGBD,
    )


def test_frame_packet_compatibility_fixture_preserves_contract_values() -> None:
    packet = make_frame_packet()

    assert packet.frame_id == "compatibility-frame-0001"
    assert packet.timestamp_ns == 1_234_567_890
    assert packet.source_type is SourceType.SYNTHETIC_RGBD
    assert packet.rgb.shape == (2, 3, 3)
    assert packet.rgb.dtype == np.uint8
    assert packet.depth_m.shape == (2, 3)
    assert packet.depth_m.dtype == np.float32
    assert packet.valid_depth_mask.shape == (2, 3)
    assert packet.valid_depth_mask.dtype == bool
    assert packet.intrinsics.shape == (3, 3)
    assert packet.intrinsics.dtype == np.float64
    assert packet.camera_to_shelf.shape == (4, 4)
    assert packet.camera_to_shelf.dtype == np.float64

    np.testing.assert_allclose(packet.depth_m[0, :2], [1.25, 0.0])
    np.testing.assert_array_equal(
        packet.intrinsics,
        np.array([[600.0, 0.0, 1.0], [0.0, 601.0, 0.5], [0.0, 0.0, 1.0]]),
    )
    np.testing.assert_allclose(
        packet.camera_to_shelf,
        np.array(
            [
                [1.0, 0.0, 0.0, 0.1],
                [0.0, 1.0, 0.0, 0.2],
                [0.0, 0.0, 1.0, 0.3],
                [0.0, 0.0, 0.0, 1.0],
            ]
        ),
    )


def test_frame_packet_compatibility_fixture_treats_invalid_depth_as_unknown() -> None:
    packet = make_frame_packet()

    np.testing.assert_array_equal(
        packet.valid_depth_mask,
        np.array(
            [[True, False, False], [True, False, False]],
            dtype=bool,
        ),
    )


def test_frame_packet_fixture_timestamp_can_be_replayed_in_monotonic_order() -> None:
    first = make_frame_packet()
    second = FramePacket(
        frame_id="compatibility-frame-0002",
        timestamp_ns=first.timestamp_ns + 1,
        rgb=first.rgb,
        depth_m=first.depth_m,
        valid_depth_mask=first.valid_depth_mask,
        intrinsics=first.intrinsics,
        camera_to_shelf=first.camera_to_shelf,
        source_type=first.source_type,
    )

    assert first.timestamp_ns < second.timestamp_ns
