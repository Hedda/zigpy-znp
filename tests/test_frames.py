import pytest

import zigpy_znp.commands as commands
import zigpy_znp.exceptions as zexc
import zigpy_znp.frames as frames
import zigpy_znp.types as t


def test_general_frame():
    data = b"\xaa\55\xccdata goes in here\x00\x00"
    length = t.uint8_t(len(data)).serialize()
    cmd = commands.Command(0x0161)

    frame = frames.GeneralFrame(cmd, data)
    assert frame.serialize() == length + b"\x61\x01" + data

    with pytest.raises(ValueError):
        frames.GeneralFrame(0, b"\x00" * 251)

    extra = b"the rest of the owl\x00\x00"
    r, rest = frames.GeneralFrame.deserialize(length + b"\x23\x00" + data + extra)
    assert rest == extra


def test_general_frame_wrong_data():
    # wrong length
    data = b"\xfb" + b"\x00" * 258
    with pytest.raises(ValueError):
        frames.GeneralFrame.deserialize(data)

    # data too short
    data = b"\x04\x00\x00"
    with pytest.raises(zexc.InvalidFrame):
        frames.GeneralFrame.deserialize(data)


def test_transport_frame():
    sof = t.uint8_t(0xFE).serialize()
    bad_sof = t.uint8_t(0xFF).serialize()
    payload = b"\x02\x61\x01\x11\x00"
    fcs = b"\x73"
    bad_fcs = b"\x74"
    extra = b"the rest of the owl\x00\xaa\x55\xff"

    r, rest = frames.TransportFrame.deserialize(sof + payload + fcs + extra)
    assert rest == extra
    assert r.serialize() == sof + payload + fcs

    # wrong SOF
    with pytest.raises(AssertionError):
        frames.TransportFrame.deserialize(bad_sof + payload + fcs + extra)

    # bad FCS
    r, rest = frames.TransportFrame.deserialize(sof + payload + bad_fcs + extra)
    assert rest == extra
    assert r.is_valid is False
