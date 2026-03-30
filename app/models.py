from sqlalchemy.orm import declarative_base, Mapped, mapped_column

Base = declarative_base()


class Build(Base):
    __tablename__ = "builds"

    id: Mapped[int] = mapped_column(primary_key=True)
    attrpath: Mapped[str]
    hydra_id: Mapped[int | None]
