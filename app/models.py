from sqlalchemy import Column, Integer


from app.database import Base


class Segment(Base):
    __tablename__ = 'segments'
    length = 3
    id = Column(Integer, primary_key=True, index=True)
    track = Column(Integer, index=True)
    position = Column(Integer)

    def __repr__(self):
        return f'{self.track}:{self.position * self.length}:{(self.position + 1) * self.length}'
