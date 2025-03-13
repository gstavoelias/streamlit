from DB.db import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean, Float, DateTime
from sqlalchemy.inspection import inspect


class Operador(Base):
    __tablename__ = "operador"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String)


class TesteFirmware(Base):
    __tablename__ = "teste_firmware"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    controladora_id: Mapped[str] = mapped_column(String)
    versao_blackpill_id: Mapped[str] = mapped_column(String)
    versao_firmware_id: Mapped[str] = mapped_column(String)
    resultado_rtc: Mapped[bool] = mapped_column(Boolean)
    resultado_serial_number: Mapped[bool] = mapped_column(Boolean)
    resultado_inclinometro: Mapped[bool] = mapped_column(Boolean)
    resultado_ponte_h: Mapped[bool] = mapped_column(Boolean)
    resultado_adc: Mapped[bool] = mapped_column(Boolean)
    horario: Mapped[DateTime] = mapped_column(DateTime)
    porta_serial: Mapped[str] = mapped_column(String)
    duracao: Mapped[float] = mapped_column(Float)
    operador_id: Mapped[int] = mapped_column(Integer)
    leituras_inclinometro: Mapped[str] = mapped_column(String)
    leituras_adc: Mapped[str] = mapped_column(String)

    def get_attr_dict(self) -> dict:
        return {
            "id": self.id,
            "controladora_id": self.controladora_id,
            "versao_blackpill_id": self.versao_blackpill_id,
            "versao_firmware_id": self.versao_firmware_id,
            "resultado_rtc": self.resultado_rtc,
            "resultado_serial_number": self.resultado_serial_number,
            "resultado_inclinometro": self.resultado_inclinometro,
            "resultado_ponte_h": self.resultado_ponte_h,
            "resultado_adc": self.resultado_adc,
            "horario": self.horario.strftime("%Y-%m-%d %H:%M:%S.%f") if self.horario else None,
            "porta_serial": self.porta_serial,
            "duracao": self.duracao,
            "operador_id": self.operador_id,
            "leituras_inclinometro": self.leituras_inclinometro,
            "leituras_adc": self.leituras_adc
        }

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}