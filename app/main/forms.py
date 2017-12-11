from flask_wtf import FlaskForm
from flask_pagedown.fields import PageDownField
from wtforms import StringField, SubmitField, BooleanField, Field, FormField, FieldList, HiddenField
from wtforms.validators import DataRequired
from wtforms.widgets import html_params, HTMLString


class ButtonWidget(object):
    """
    Renders a multi-line text area.
    `rows` and `cols` ought to be passed as keyword args when rendering.
    """
    input_type = 'button'

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

    def __init__(self, flashcard=None):
        super().__init__()
        self.answer.data = flashcard.answer if flashcard is not None else self.answer.data
        self.question.data = flashcard.question if flashcard is not None else self.question.data
        self.hint1.data = flashcard.hint1 if flashcard is not None else self.hint1.data
        self.hint2.data = flashcard.hint2 if flashcard is not None else self.hint2.data
        self.hint3.data = flashcard.hint3 if flashcard is not None else self.hint3.data


class AddFlashcardForm(FlashcardForm):
    next = BooleanField('Next Flashcard?')
    submit = SubmitField('Add')
    hint = ButtonField('Add Hint')


class EditFlashcardForm(FlashcardForm):
    submit = SubmitField('edit')
    hint = ButtonField('Add Hint')

    def get_hint_amount(self):
        hint_counter = 0
        if self.hint1.data != '':
            hint_counter += 1
        if self.hint2.data != '':
            hint_counter += 1
        if self.hint3.data != '':
            hint_counter += 1
        return hint_counter
