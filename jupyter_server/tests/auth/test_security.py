from jupyter_server.auth.security import passwd
from jupyter_server.auth.security import passwd_check


def test_passwd_structure():
    p = passwd("passphrase")
    algorithm, hashed = p.split(":")
    assert algorithm == "argon2", algorithm
    assert hashed.startswith("$argon2id$"), hashed


def test_roundtrip():
    p = passwd("passphrase")
    assert passwd_check(p, "passphrase")


def test_bad():
    p = passwd("passphrase")
    assert not passwd_check(p, p)
    assert not passwd_check(p, "a:b:c:d")
    assert not passwd_check(p, "a:b")


def test_passwd_check_unicode():
    # GH issue #4524
    phash = u"sha1:23862bc21dd3:7a415a95ae4580582e314072143d9c382c491e4f"
    assert passwd_check(phash, u"łe¶ŧ←↓→")
    phash = (
        u"argon2:$argon2id$v=19$m=10240,t=10,p=8$" u"qjjDiZUofUVVnrVYxacnbA$l5pQq1bJ8zglGT2uXP6iOg"
    )
    assert passwd_check(phash, u"łe¶ŧ←↓→")
