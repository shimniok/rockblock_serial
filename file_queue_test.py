import os
from pathlib import Path
import pytest
from test_fixture import app
from file_queue import FileQueue

q_dir = "/tmp/q"


@pytest.fixture(scope='session')
def queue(app):

    q = FileQueue(q_dir)
    assert q

    yield q

    for f in os.listdir(q_dir):
        os.remove("{d}/{f}".format(d=q_dir, f=f))
    os.removedirs(q_dir)
    assert not os.path.exists(q_dir)

def test_directory(queue):
    assert os.path.exists(q_dir)
    assert queue.get_directory() == q_dir

def test_messages_empty(queue):
    m = queue.get_messages()
    assert len(m) == 0

def test_filter(queue):
    names = [
        '01234567-012345+012345.txt', # should match
        '012345678-012345+012345.txt', # all the rest should not match
        '01234567-0123456+012345.txt',
        '01234567-012345+0123456.txt',
        '0123456-012345+012345.txt',
        '01234567-01234+012345.txt',
        '01234567-012345+01234.txt',
        '01234567-012345+012345.txta',
        'a01234567-012345+012345.txt',
        '01234567x012345+012345.txt',
        '01234567-012345x012345.txt',
        '01234567-012345+012345xtxt'
    ]

    for f in names:
        Path("{d}/{f}".format(d=q_dir, f=f)).touch(mode=664, exist_ok=True)

    m = queue.get_messages()
    assert len(m) == 1

    for f in names:
        os.remove("{d}/{f}".format(d=q_dir, f=f))

def test_enqueue_dequeue(queue):
    text = "testing"
    queue.enqueue_message(text)
    assert len(queue.get_messages()) == 1
    
    m = queue.dequeue_message()
    assert m == text
    assert len(queue.get_messages()) == 0
