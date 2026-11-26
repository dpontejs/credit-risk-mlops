import credit_risk


def test_version_is_exposed() -> None:
    assert isinstance(credit_risk.__version__, str)
    assert credit_risk.__version__
