from ugt_fwtools import utils


def test_build_t():
    assert utils.build_t("42") == "0042"
    assert utils.build_t("1234") == "1234"
    assert utils.build_t("0x1234") == "1234"
