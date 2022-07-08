import jwt

from gateway import auth


def test_make_token(private_key, public_key):
    algo = "RS256"
    token = auth.make_token("chain_id", private_key, algo)
    decoded = jwt.decode(token, public_key, algorithms=[algo])
    assert decoded["sub"] == "chain_id"
