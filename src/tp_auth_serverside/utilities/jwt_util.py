import logging
from datetime import UTC, datetime, timedelta

import jwt

from tp_auth_serverside.config import Secrets, SupportedAlgorithms


class JWTUtil:
    def __init__(
        self,
        token_type: str = "access",
        algorithm: SupportedAlgorithms = None,
        write_key: str = None,
        read_key: str = None,
    ) -> None:
        self.token_type = token_type
        self.algorithm = algorithm or Secrets.algorithm
        if self.algorithm == SupportedAlgorithms.RS256:
            self.read_key = read_key or Secrets.public_key
            if Secrets.authorization_server or write_key:
                self.write_key = write_key or Secrets.private_key
            else:
                self.write_key = None
        elif self.algorithm == SupportedAlgorithms.HS256:
            self.read_key = read_key or Secrets.secret_key
            self.write_key = write_key or Secrets.secret_key

    def encode(self, payload: dict, exp_time: int = None) -> str:
        try:
            payload |= {
                "iss": Secrets.issuer,
                "exp": datetime.now(UTC) + timedelta(minutes=exp_time or Secrets.expiry),
                "iat": datetime.now(UTC),
                "token_type": self.token_type,
            }
            return jwt.encode(payload, self.write_key, algorithm=self.algorithm)
        except Exception as e:
            logging.error(f"Error encoding token: {e}")
            raise e

    def decode(self, token: str) -> dict:
        try:
            return jwt.decode(token, self.read_key, algorithms=[self.algorithm])
        except Exception as e:
            logging.error(f"Error decoding token: {e}")
            raise e

    def verify(self, token: str) -> bool:
        try:
            jwt.decode(token, self.read_key, algorithms=[self.algorithm])
            return True
        except jwt.InvalidSignatureError as e:
            logging.error(f"Invalid signature: {e}")
            return False
        except jwt.ExpiredSignatureError as e:
            logging.error(f"Expired signature: {e}")
            return False
        except jwt.InvalidTokenError as e:
            logging.error(f"Invalid token: {e}")
            return False
        except Exception as e:
            logging.error(f"Error verifying token: {e}")
            raise e
