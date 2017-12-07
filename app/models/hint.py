from .. import db
from markdown import markdown
import bleach

# class Hint(db.Model):
#     __tablename__ = 'hint'
#     id = db.Column(db.Integer, primary_key=True)
#     hint = db.Column(db.Text)
#     hint_html = db.Column(db.Text)
#     flashcard_id = db.Column(db.Integer, db.ForeignKey('flashcard.id'))
#
#     @staticmethod
#     def on_changed_hint(target, value, oldvalue, initiator):
#         allowed_tags = ['abbr', 'acronym', 'b', 'blockquote', 'code', 'i',
#                         'li', 'ol', 'strong', 'ul', 'h1', 'h2', 'h3', 'p']
#         # target.question_html = bleach.clean(markdown(value, output_format='html'), tags=allowed_tags, strip=True)
#         target.hint_html = value
#
#     # Method is an override to tell python how to print this.
#     def __repr__(self):
#         return '<Hint: %r>' % self.id
#
#
# db.event.listen(Hint.hint, 'set', Hint.on_changed_hint)
