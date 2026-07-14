"""
backend/db/models.py

ORM(Object Relational Mapper) model definitions: Ticket, Classification, Draft, AuditLog.
"""

from __future__ import annotations

from sqlalchemy import (
    Column,
    String,
    Float,
    Boolean,
    Integer,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id = Column(String, primary_key=True)
    raw_text = Column(Text, nullable=False)
    status = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, index=True)
    updated_at = Column(
        DateTime, nullable=False
    )  # nullable=false means, This field cannot be empty.

    # One Ticket -> one Classification, one Draft, many AuditLog
    # entries. uselist=False means "give me back a single object,
    # not a list" for the one-to-one relationships.
    # Classification" → The target ORM model.
    classification = relationship(
        "Classification", back_populates="ticket", uselist=False
    )
    draft = relationship("Draft", back_populates="ticket", uselist=False)
    audit_logs = relationship("AuditLog", back_populates="ticket")


class Classification(Base):
    __tablename__ = "classification"

    ticket_id = Column(String, ForeignKey("tickets.ticket_id"), primary_key=True)
    equipment_id = Column(String)
    fault_type = Column(String)
    urgency = Column(String)
    confidence = Column(Float)
    safety_override_applied = Column(Boolean, default=False)

    ticket = relationship("Ticket", back_populates="classification")


class Draft(Base):
    __tablename__ = "draft"

    ticket_id = Column(String, ForeignKey("tickets.ticket_id"), primary_key=True)
    recommendation = Column(Text)
    human_decision = Column(String)
    human_feedback = Column(Text)

    ticket = relationship("Ticket", back_populates="draft")


class AuditLog(Base):
    __tablename__ = "audit_log"

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(String, ForeignKey("tickets.ticket_id"), index=True)
    step_name = Column(String, nullable=False)
    input_snapshot = Column(Text)
    output_snapshot = Column(Text)
    timestamp = Column(DateTime, nullable=False)

    ticket = relationship("Ticket", back_populates="audit_logs")
