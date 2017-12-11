import datetime

from .. import db
from markdown import markdown
import bleach

import math


class Flashcard(db.Model):
    __tablename__ = 'flashcard'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text)
    question_html = db.Column(db.Text)
    answer = db.Column(db.Text)
    answer_html = db.Column(db.Text)
    hint1 = db.Column(db.Text)
    hint1_html = db.Column(db.Text)
    hint2 = db.Column(db.Text)
    hint2_html = db.Column(db.Text)
    hint3 = db.Column(db.Text)
    hint3_html = db.Column(db.Text)
    repetitions = db.Column(db.Integer, default=0)
    interval = db.Column(db.Integer, default=1)
    easiness = db.Column(db.Integer, default=2.5)
    time = db.Column(db.DateTime, default=datetime.datetime.now())
    next_time = db.Column(db.DateTime)
    collection_id = db.Column(db.Integer, db.ForeignKey('flashcardcollection.id'))

    allowed_tags = ['abbr', 'acronym', 'b', 'blockquote', 'code', 'i',
                    'li', 'ol', 'strong', 'ul', 'h1', 'h2', 'h3', 'p', 'img']

    allowed_attrs = {'*': ['class'],
                     'a': ['href', 'rel'],
                     'img': ['src', 'alt']}

    def is_new(self):
        return self.repetitions == 0

    def calc_next_time(self):
        return self.time + datetime.timedelta(days=math.ceil(self.interval))

    def repeat(self, performance, time):
        self.easiness = max(1.3, self.easiness + 0.1 - (5.0 - performance) * (0.08 + (5.0 - performance) * 0.02))
        if performance < 3:
            self.repetitions = 0
        else:
            self.repetitions += 1
        if self.repetitions == 1:
            self.interval = 1
        elif self.repetitions == 2:
            self.interval = 6
        else:
            self.interval *= self.easiness
        self.time = time
        self.next_time = self.calc_next_time()

    @staticmethod
    def on_changed_question(target, value, oldvalue, initiator):
        target.question_html = bleach.clean(markdown(value, output_format='html'),
                                            tags=Flashcard.allowed_tags,
                                            attributes=Flashcard.allowed_attrs,
                                            strip=True)

    @staticmethod
    def on_changed_answer(target, value, oldvalue, initiator):
        target.answer_html = bleach.clean(markdown(value, output_format='html'),
                                          tags=Flashcard.allowed_tags,
                                          attributes=Flashcard.allowed_attrs,
                                          strip=True)

    @staticmethod
    def on_changed_hint1(target, value, oldvalue, initiator):
        target.hint1_html = bleach.clean(markdown(value, output_format='html'),
                                         tags=Flashcard.allowed_tags,
                                         attributes=Flashcard.allowed_attrs,
                                         strip=True)

    @staticmethod
    def on_changed_hint2(target, value, oldvalue, initiator):
        target.hint2_html = bleach.clean(markdown(value, output_format='html'),
                                         tags=Flashcard.allowed_tags,
                                         attributes=Flashcard.allowed_attrs,
                                         strip=True)

    @staticmethod
    def on_changed_hint3(target, value, oldvalue, initiator):
        target.hint3_html = bleach.clean(markdown(value, output_format='html'),
                                         tags=Flashcard.allowed_tags,
                                         attributes=Flashcard.allowed_attrs,
                                         strip=True)

    def __repr__(self):
        return '<Flashcard: %r>' % self.id


db.event.listen(Flashcard.question, 'set', Flashcard.on_changed_question)
db.event.listen(Flashcard.answer, 'set', Flashcard.on_changed_answer)
db.event.listen(Flashcard.hint1, 'set', Flashcard.on_changed_hint1)
db.event.listen(Flashcard.hint2, 'set', Flashcard.on_changed_hint2)
db.event.listen(Flashcard.hint3, 'set', Flashcard.on_changed_hint3)
