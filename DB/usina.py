from DB.models import TesteFirmware
from DB.db import SessionLocal
from dataclasses import asdict

class Usina:
    def __init__(self):
        self._session = SessionLocal()

    def get_teste_firmware(self) -> list[dict]:
        tests = self._session.query(TesteFirmware).limit(50)
        data = [test.to_dict() for test in tests]
        return data
    
if __name__ == "__main__":
    usina = Usina()
    print(usina.get_teste_firmware())  