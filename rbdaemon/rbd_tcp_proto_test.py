import pytest
from test_fixture import app
from rbd_tcp_proto import RockBlockDaemonProtocol


@pytest.fixture(scope='module')
def proto(app):
    p = RockBlockDaemonProtocol()
    yield p

def test_parse(proto):
    event, args = proto.parse("A message")
    assert not event and not args
    event, args = proto.parse("M message")
    assert event == "M" and args == "message"
    event, args = proto.parse("E error")
    assert event == "E" and args == "error"
    event, args = proto.parse("S 6") # signal is 0-5
    assert event == None and args == None
    event, args = proto.parse("S 00")  # signal is 0-5
    assert event == None and args == None
    event, args = proto.parse("S 05")  # signal is 0-5
    assert event == None and args == None
    event, args = proto.parse("S a")  # signal is 0-5
    assert event == None and args == None
    event, args = proto.parse("S 5")  # signal is 0-5
    assert event == "S" and args == 5
    event, args = proto.parse("S 0")  # signal is 0-5
    assert event == "S" and args == 0
