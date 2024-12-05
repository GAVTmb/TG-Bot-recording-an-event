import datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Date, ForeignKey


class Base(DeclarativeBase):
    ...


class Event(Base):
    __tablename__ = "event"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name_event: Mapped[str] = mapped_column(String(150), nullable=False)
    description_event: Mapped[str] = mapped_column(Text, nullable=True)
    image: Mapped[str] = mapped_column(String(300), nullable=False)
    price: Mapped[int] = mapped_column(nullable=False)
    beginning_event: Mapped[Date] = mapped_column(Date, nullable=False)
    the_end_event: Mapped[Date] = mapped_column(Date, nullable=False)
    location_event: Mapped[str] = mapped_column(String(300), nullable=True)
    number_participants: Mapped[int] = mapped_column(nullable=False)


class Participant(Base):
    __tablename__ = "participant"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("event.id", ondelete="CASCADE"), nullable=False)
    tg_user_id: Mapped[str] = mapped_column(String(30), unique= False, nullable=False)
    surname: Mapped[str] = mapped_column(String(30), nullable=False)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    # payment: Mapped[bool] = mapped_column(nullable=False)

    event: Mapped["Event"] = relationship(backref="participant")


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    participant_id: Mapped[int] = mapped_column(ForeignKey("participant.id", ondelete="CASCADE"), nullable=False)
    public_feedback: Mapped[str] = mapped_column(Text, nullable=True)
    closed_feedback: Mapped[str] = mapped_column(Text, nullable=True)

    participant: Mapped["Participant"] = relationship(backref="feedback")
