from .. import db
from markdown import markdown
import bleach


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
    right_answered = db.Column(db.Boolean, default=False)
    wrong_answered = db.Column(db.Boolean, default=False)
    collection_id = db.Column(db.Integer, db.ForeignKey('flashcardcollection.id'))

    allowed_tags = ['abbr', 'acronym', 'b', 'blockquote', 'code', 'i',
                    'li', 'ol', 'strong', 'ul', 'h1', 'h2', 'h3', 'p', 'img']

    allowed_attrs = {'*': ['class'],
                     'a': ['href', 'rel'],
                     'img': ['src', 'alt']}

    # hints = db.relationship('Hint', backref='collection', lazy='dynamic')

    @staticmethod
    def on_changed_question(target, value, oldvalue, initiator):
        target.question_html = bleach.clean(markdown(value, output_format='html'),
                                            tags=Flashcard.allowed_tags,
                                            attributes=Flashcard.allowed_attrs,
                                            strip=True)
        i = 1
        # target.question_html = value

    @staticmethod
    def on_changed_answer(target, value, oldvalue, initiator):
        target.answer_html = bleach.clean(markdown(value, output_format='html'),
                                          tags=Flashcard.allowed_tags,
                                          attributes=Flashcard.allowed_attrs,
                                          strip=True)
        # target.answer_html = value

    @staticmethod
    def on_changed_hint1(target, value, oldvalue, initiator):
        target.hint1_html = bleach.clean(markdown(value, output_format='html'),
                                         tags=Flashcard.allowed_tags,
                                         attributes=Flashcard.allowed_attrs,
                                         strip=True)
        # target.hint1_html = value

    @staticmethod
    def on_changed_hint2(target, value, oldvalue, initiator):
        target.hint2_html = bleach.clean(markdown(value, output_format='html'),
                                         tags=Flashcard.allowed_tags,
                                         attributes=Flashcard.allowed_attrs,
                                         strip=True)
        # target.hint2_html = value

    @staticmethod
    def on_changed_hint3(target, value, oldvalue, initiator):
        target.hint3_html = bleach.clean(markdown(value, output_format='html'),
                                         tags=Flashcard.allowed_tags,
                                         attributes=Flashcard.allowed_attrs,
                                         strip=True)
        # target.hint3_html = value

    def __repr__(self):
        return '<Flashcard: %r>' % self.id


db.event.listen(Flashcard.question, 'set', Flashcard.on_changed_question)
db.event.listen(Flashcard.answer, 'set', Flashcard.on_changed_answer)
db.event.listen(Flashcard.hint1, 'set', Flashcard.on_changed_hint1)
db.event.listen(Flashcard.hint2, 'set', Flashcard.on_changed_hint2)
db.event.listen(Flashcard.hint3, 'set', Flashcard.on_changed_hint3)
