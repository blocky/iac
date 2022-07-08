import jwt


def make_token(chain_id: str, private_key: str, algo: str):
    """
    Create a token in the expected format.  Strictly speaking, this code is
    not used by this project, but is used in many tests.  Within the context of
    Zipperchain, the token would be created by zpr for a specific chain.
    """
    return jwt.encode({"sub": chain_id}, private_key, algorithm=algo)
