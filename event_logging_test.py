import os
import re
import pytest
from test_fixture import app
from event_logging import EventLog

logfile = "/tmp/test.log"
t = "test"


def line_count(file):
    count = -1
    try:
        with open(file) as f:
            lines = f.readlines()
            count = len(lines)
            f.close()
    except:
        return -2
    return count


@pytest.fixture(scope='function')
def evlog(app):

    el = EventLog(filename=logfile, level=EventLog.DEBUG)
    assert line_count(logfile) == 0
    assert el.get_level() == EventLog.DEBUG

    yield el

    os.remove(logfile)


def test__log(evlog):
    e = "<<<testing>>>"
    evlog._log(e)
    assert line_count(logfile) == 1
    with open(logfile) as f:
        pts = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (.*)\n$')
        lines = f.readlines()
        m = pts.match(lines[0])
        assert m
        assert m.group(0) == lines[0]
        assert m.group(1)
        assert m.group(2) == e
        f.close()


def test_silent_level(evlog):
    evlog.set_level(EventLog.SILENT)
    evlog.debug(t)
    evlog.info(t)
    evlog.warning(t)
    evlog.error(t)
    assert line_count(logfile) == 0


def test_error_level(evlog):
    evlog.set_level(EventLog.ERROR)
    evlog.debug(t)
    evlog.info(t)
    evlog.warning(t)
    evlog.error(t)
    assert line_count(logfile) == 1

def test_warning_level(evlog):
    evlog.set_level(EventLog.WARNING)
    evlog.debug(t)
    evlog.info(t)
    evlog.warning(t)
    evlog.error(t)
    assert line_count(logfile) == 2

def test_info_level(evlog):
    evlog.set_level(EventLog.INFO)
    evlog.debug(t)
    evlog.info(t)
    evlog.warning(t)
    evlog.error(t)
    assert line_count(logfile) == 3

def test_debug_level(evlog):
    evlog.set_level(EventLog.DEBUG)
    evlog.debug(t)
    evlog.info(t)
    evlog.warning(t)
    evlog.error(t)
    assert line_count(logfile) == 4
