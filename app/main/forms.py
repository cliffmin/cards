from flask_wtf import FlaskForm
from flask_pagedown.fields import PageDownField
from wtforms import StringField, SubmitField, BooleanField, Field, FormField, FieldList
from wtforms.validators import DataRequired
from wtforms.widgets import html_params, HTMLString


class ButtonWidget(object):
    """
    Renders a multi-line text area.
    `rows` and `cols` ought to be passed as keyword args when rendering.
    """
    input_type = 'submit'

    html_params = staticmethod(html_params)

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        if 'value' not in kwargs:
            kwargs['value'] = field._value()

        return HTMLString('<button {params}>{label}</button>'.format(
            params=self.html_params(name=field.name, **kwargs),
            label=field.label.text)
        )


class ButtonField(StringField):
    widget = ButtonWidget()


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


class HintForm(FlaskForm):
    hint = PageDownField('Hint')


class EditFlashcardForm(FlaskForm):
    hints = None
    hint_amount = 0

    def __init__(self, flashcard):
        self.answer = flashcard.answer
        self.question = flashcard.question
        self.hint_amount = flashcard.hint_amount
        self.hints = FieldList(FormField(HintForm), min_entries=self.hint_amount, max_entries=5)
        super().__init__()

    question = PageDownField('Question', validators=[DataRequired()])
    answer = PageDownField('Answer', validators=[DataRequired()])
    submit_btn = SubmitField('Edit')
    hint_btn = SubmitField('Add a Hint')
