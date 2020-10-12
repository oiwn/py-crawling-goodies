"""Test patterns"""
from pcg.patterns.singleton import Singleton


def test_singleton():
    """testing singleton pattern"""

    class Obj(metaclass=Singleton):  # pylint: disable=R0903
        """Test Obj class"""

    class AnotherObj:  # pylint: disable=R0903
        """Another obj"""

    first_instance = Obj()
    second_instance = Obj()
    another_instance = AnotherObj()

    assert first_instance == second_instance
    assert first_instance != another_instance
