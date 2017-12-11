import datetime

from sqlalchemy import desc, and_

from app.models.flashcard import Flashcard
from .. import db
from .hascategory import has_category


class FlashcardCollection(db.Model):
    __tablename__ = 'flashcardcollection'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    flashcards = db.relationship('Flashcard', backref='collection', lazy='dynamic')
    categories = db.relationship('Category',
                                 secondary=has_category,
                                 backref=db.backref('collections', lazy='dynamic'),
                                 lazy='dynamic')

    def get_new_card_ids(self):
        ids = db.session.query(Flashcard.id) \
            .filter(and_(Flashcard.collection_id == self.id, Flashcard.repetitions == 0)) \
            .order_by(desc(Flashcard.time)).all()
        return [i.id for i in ids]

    def get_reviewed_card_ids(self):
        ids = db.session.query(Flashcard.id) \
            .filter(and_(Flashcard.collection_id == self.id, Flashcard.repetitions != 0)) \
            .order_by(desc(Flashcard.next_time)).all()
        return [i.id for i in ids]

    def __repr__(self):
        return '<Flashcard Collection: %r>' % self.name
