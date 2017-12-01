from flask_wtf import FlaskForm
from flask_pagedown.fields import PageDownField
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired


class FlashcardCollectionForm(FlaskForm):
    name = StringField('Collection name', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    submit = SubmitField('Add')


class FlashcardForm(FlaskForm):
    question = PageDownField('Question', validators=[DataRequired()])
    answer = PageDownField('Answer', validators=[DataRequired()])
    hint1 = PageDownField('Hint 1')
    hint2 = PageDownField('Hint 2')
    hint3 = PageDownField('Hint 3')
    next = BooleanField('Next Flashcard?')
    submit = SubmitField('Add')


class EditFlashcardForm(FlaskForm):
    question = PageDownField('Question', validators=[DataRequired()])
    answer = PageDownField('Answer', validators=[DataRequired()])
    hint1 = PageDownField('Hint 1')
    hint2 = PageDownField('Hint 2')
    hint3 = PageDownField('Hint 3')
    submit = SubmitField('Edit')
