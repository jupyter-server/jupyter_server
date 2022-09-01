import json
import os
import uuid
from datetime import datetime
from sqlite3 import OperationalError

import sqlalchemy.types as types
from jupyter_scheduling.models import EmailNotifications, Status
from jupyter_scheduling.utils import create_output_filename, get_utc_timestamp
from sqlalchemy import Boolean, Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, registry, sessionmaker

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())


def generate_url(context) -> str:
    job_id = context.get_current_parameters()["job_id"]
    return f"/jobs/{job_id}"


def output_uri(context) -> str:
    input_uri = context.get_current_parameters()["input_uri"]
    output_prefix = context.get_current_parameters()["output_prefix"]
    output_formats = context.get_current_parameters()["output_formats"]

    if not output_formats or "ipynb" in output_formats:
        output_filename = create_output_filename(input_uri)
    else:
        output_filename = create_output_filename(
            os.path.splitext(input_uri)[-2] + "." + output_formats[0]
        )

    return os.path.join(output_prefix, output_filename)


class JsonType(types.TypeDecorator):
    impl = String

    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None

        return json.loads(value)


class EmailNotificationType(types.TypeDecorator):
    impl = String

    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None

        if isinstance(value, EmailNotifications):
            return json.dumps(value.dict(exclude_none=True))
        else:
            return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return EmailNotifications.construct(json.loads(value))


mapper_registry = registry()


class Job(Base):
    __tablename__ = "jobs"
    job_id = Column(String(36), primary_key=True, default=generate_uuid)
    runtime_environment_name = Column(String(256), nullable=False)
    runtime_environment_parameters = Column(JsonType(1024))
    compute_type = Column(String(256), nullable=True)
    input_uri = Column(String(256), nullable=False)
    output_prefix = Column(String(256))
    output_formats = Column(JsonType(512))
    output_uri = Column(String(256), default=output_uri)
    name = Column(String(256))
    job_definition_id = Column(String(36))
    idempotency_token = Column(String(256))
    status = Column(String(64), default=Status.STOPPED)
    tags = Column(JsonType(1024))
    status_message = Column(String(1024))
    start_time = Column(Integer)
    end_time = Column(Integer)
    parameters = Column(JsonType(1024))
    url = Column(String(256), default=generate_url)
    email_notifications = Column(EmailNotificationType(1024))
    timeout_seconds = Column(Integer, default=600)
    retry_on_timeout = Column(Boolean, default=False)
    max_retries = Column(Integer, default=0)
    min_retry_interval_millis = Column(Integer, default=0)
    output_filename_template = Column(String(256))
    pid = Column(Integer)
    update_time = Column(Integer, default=get_utc_timestamp, onupdate=get_utc_timestamp)


def create_tables(db_url, drop_tables=False):
    engine = create_engine(db_url)
    try:
        if drop_tables:
            Base.metadata.drop_all(engine)
    except OperationalError:
        pass
    finally:
        Base.metadata.create_all(engine)


def create_session(db_url):
    engine = create_engine(db_url, echo=True)
    Session = sessionmaker(bind=engine)

    return Session
