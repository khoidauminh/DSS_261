from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey   

class Base(DeclarativeBase):
    pass

class University(Base):
    __tablename__ = "universities"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)

class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    university_id: Mapped[int] = mapped_column(ForeignKey(f"{University.__tablename__}.id"))

    university: Mapped['University'] = relationship(back_populates=University.__tablename__)
    