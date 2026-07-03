from sqlalchemy import Column, Integer, String, DateTime, LargeBinary
from sqlalchemy.orm import Session
from datetime import datetime
from io import BytesIO
from app.database.db import Base, engine
import matplotlib.pyplot as plt


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    data = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, default=datetime.now)


def save_image(fig: plt.Figure, plot_name: str):
    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    buffer.seek(0)
    image_data = buffer.read()
    buffer.close()

    with Session(engine) as session:
        img = Image(
            filename=plot_name,
            mime_type="image/png",
            data=image_data,
        )
        session.add(img)
        session.commit()
        return img.id


def get_image(id: int):
    with Session(engine) as session:
        img = session.get(Image, id)
        if img:
            return {
                "filename": img.filename,
                "mime_type": img.mime_type,
                "data": img.data,
            }
        return None
