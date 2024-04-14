import enum
import sqlalchemy.orm as orm
import sqlalchemy as sqa

from datetime import datetime, date


class Base(orm.DeclarativeBase):
    pass


class Role(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"


class User(Base):
    __tablename__ = 'users'

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    username: orm.Mapped[str] = orm.mapped_column(sqa.String(100), index=True)
    email: orm.Mapped[str] = orm.mapped_column(sqa.String(100), unique=True, nullable=False)
    password: orm.Mapped[str] = orm.mapped_column(sqa.String(250), nullable=False)
    avatar: orm.Mapped[str] = orm.mapped_column(sqa.String(250), nullable=True)
    refresh_token: orm.Mapped[str] = orm.mapped_column(sqa.String(250), nullable=True)
    is_active: orm.Mapped[bool] = orm.mapped_column(default=True)
    created_at: orm.Mapped[datetime] = orm.mapped_column(sqa.DateTime, default=sqa.func.now())
    updated_at: orm.Mapped[datetime] = orm.mapped_column(sqa.DateTime, default=sqa.func.now(), onupdate=sqa.func.now())
    role: orm.Mapped[sqa.Enum] = orm.mapped_column('role', sqa.Enum(Role), default=Role.user, nullable=True)
    confirmed: orm.Mapped[bool] = orm.mapped_column(sqa.Boolean, default=False, nullable=True)

class Contact(Base):
    __tablename__ = 'contacts'

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    first_name: orm.Mapped[str] = orm.mapped_column(sqa.String(50), index=True)
    last_name: orm.Mapped[str] = orm.mapped_column(sqa.String(50), index=True)
    email: orm.Mapped[str] = orm.mapped_column(sqa.String(50), index=True)
    phone_number: orm.Mapped[str] = orm.mapped_column(sqa.String(50))
    date_of_birth: orm.Mapped[date] = orm.mapped_column(sqa.Date)
    additional_data: orm.Mapped[str] = orm.mapped_column(sqa.String(250))
    created_at: orm.Mapped[date] = orm.mapped_column("created_at", sqa.DateTime, default=sqa.func.now(), nullable=True)
    updated_at: orm.Mapped[date] = orm.mapped_column("updated_at", sqa.DateTime, default=sqa.func.now(),
                                                     onupdate=sqa.func.now(), nullable=True)
    user_id: orm.Mapped[int] = orm.mapped_column(sqa.Integer, sqa.ForeignKey("users.id"), nullable=True)
    user: orm.Mapped["User"] = orm.relationship("User", backref="contacts", lazy="joined")
