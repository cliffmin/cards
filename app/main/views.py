from contextlib import contextmanager
from enum import Enum

import datetime

import math
from flask import render_template, redirect, url_for, abort, flash, jsonify, make_response, request, current_app
from flask_login import login_required, current_user
from flask_sqlalchemy import get_debug_queries
from sqlalchemy import desc
from ..models.users import User
from ..models.category import Category
from ..models.flashcard_collections import FlashcardCollection
from ..models.flashcard import Flashcard
from . import main
from .. import db
from .forms import FlashcardCollectionForm, AddFlashcardForm, EditFlashcardForm
from flask import g


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASHCARD_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n' %
                (query.statement, query.parameters, query.duration, query.context))
    return response


@main.route('/')
def index():
    if current_user.is_authenticated:
        collections = current_user.collections.order_by(FlashcardCollection.timestamp.desc()).all()
    else:
        collections = []
    return render_template('index.html', collections=collections)


@main.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    collections = current_user.collections.order_by(FlashcardCollection.timestamp.desc()).all()
    return render_template('user.html', user=user, collections=collections)


@main.route('/add-collection', methods=['GET', 'POST'])
@login_required
def add_collection():
    form = FlashcardCollectionForm()
    if form.validate_on_submit():
        category = Category.query.filter_by(name=form.category.data).first()
        if category is None:
            category = Category(name=form.category.data)
        collection = FlashcardCollection(name=form.name.data)
        collection.categories.append(category)
        collection.user = current_user
        db.session.add(collection)
        db.session.commit()
        flash('Flashcard Collection added.')
        return redirect(url_for('.index'))
    return render_template('add_collection.html', form=form)


@main.route('/get-category', methods=['GET', 'POST'])
@login_required
def get_category():
    return jsonify({
        'category': [category.name for category in Category.query.order_by(Category.name).all()]
    })


@main.route('/flashcardcollection/<int:collId>')
@login_required
def flashcardcollection(collId):
    flashcardcollection = FlashcardCollection.query.get_or_404(collId)
    return render_template('flashcardcollection.html', flashcardcollection=flashcardcollection)


@main.route('/flashcardcollection/<int:collId>/delete')
@login_required
def delete_flashcardcollection(collId):
    flashcardcollection = FlashcardCollection.query.get_or_404(collId)
    db.session.delete(flashcardcollection)
    db.session.commit()
    flash('Flashcardcollection {0} has been deleted'.format(flashcardcollection.name))
    return redirect(request.referrer)


@main.route('/flashcardcollection/<int:collId>/add-flashcard', methods=['GET', 'POST'])
@login_required
def add_flashcard(collId):
    form = AddFlashcardForm()
    flashcardcollection = FlashcardCollection.query.get_or_404(collId)
    if request.method == 'POST' and form.validate_on_submit():
        card = Flashcard(question=form.question.data,
                         answer=form.answer.data,
                         hint1=form.hint1.data,
                         hint2=form.hint2.data,
                         hint3=form.hint3.data)
        flashcardcollection.flashcards.append(card)
        db.session.add(flashcardcollection)
        db.session.commit()
        flash('Flashcard added to the Collection {0}'.format(flashcardcollection.name))
        if form.next.data:
            return redirect(url_for('.add_flashcard', collId=flashcardcollection.id))
        else:
            return redirect(url_for('.flashcardcollection', collId=flashcardcollection.id))
    return render_template('add_flashcard.html', form=form, name=flashcardcollection.name)


@main.route('/flashcardcollection/<int:collId>/flashcard/<int:cardId>')
@login_required
def flashcard(collId, cardId):
    flashcardcollection = FlashcardCollection.query.get_or_404(collId)
    flashcard = flashcardcollection.flashcards.filter_by(id=cardId).first()
    if flashcard is None:
        abort(404)
    return render_template('flashcard.html', flashcardcollection=flashcardcollection, flashcard=flashcard)


@main.route('/flashcardcollection/<int:collId>/flashcard/<int:cardId>/edit', methods=['GET', 'POST'])
@login_required
def edit_flashcard(collId, cardId):
    flashcardcollection = FlashcardCollection.query.get_or_404(collId)
    flashcard = flashcardcollection.flashcards.filter_by(id=cardId).first()
    form = EditFlashcardForm()
    if flashcard is None:
        abort(404)
    if request.method == 'POST' and form.validate_on_submit():
        flashcard.question = form.question.data
        flashcard.answer = form.answer.data
        flashcard.hint1 = form.hint1.data
        flashcard.hint2 = form.hint2.data
        flashcard.hint3 = form.hint3.data
        db.session.add(flashcard)
        db.session.commit()
        flash('Flashcard was updated.')
        return redirect(url_for('.flashcard', collId=collId, cardId=cardId))
    form = EditFlashcardForm(flashcard)
    return render_template('edit_flashcard.html', form=form)


@main.route('/flashcardcollection/<int:collId>/learn')
@login_required
def learn(collId):
    flashcardcollection = FlashcardCollection.query.get_or_404(collId)
    mode = request.args.get('mode')
    cardId = int(request.args.get('cardId'))
    percent_done = 0 if 'percent_done' not in request.args else request.args.get('percent_done')

    if cardId == 0:
        Cards.init(collId)
        percent_done, cardId = Cards.choose_next()
    elif cardId < 0:
        flash('No Cards to learn. Please reset the Cards or learn the Wrong ones if there are any.')
        return redirect(url_for('.flashcardcollection', collId=collId))

    flashcard = Flashcard.query.get_or_404(cardId)

    return render_template('learn.html',
                           flashcard=flashcard,
                           collection=flashcardcollection,
                           percent_done=percent_done,
                           mode=mode)


@main.route('/flashcardcollection/<int:collId>/reset-cards')
@login_required
def reset_cards(collId):
    coll = FlashcardCollection.query.get_or_404(collId)
    for card in coll.flashcards.all():
        card.interval = 0
        card.repetitions = 0
        card.easiness = 0
        card.time = datetime.datetime.now()
        card.next_time = None
    db.session.add(coll)
    db.session.commit()
    return redirect(url_for('.flashcardcollection', collId=collId))


@main.route('/flashcardcollection/<int:collId>/delete-flashcard/<int:cardId>')
@login_required
def delete_card(collId, cardId):
    flashcard = Flashcard.query.get_or_404(cardId)
    db.session.delete(flashcard)
    db.session.commit()
    return redirect(url_for('.flashcardcollection', collId=collId))


@main.route('/flashcardcollection/<int:collId>/learn/<int:cardId>/result')
@login_required
def result(collId, cardId):
    flashcard = db.session.query(Flashcard).filter_by(id=cardId).first()
    performance = request.args.get('performance')
    flashcard.repeat(Performance[performance].value, datetime.datetime.now())
    db.session.add(flashcard)
    db.session.commit()
    percent_done, cardId = Cards.choose_next()
    # db.session.expunge(flashcard)
    # db.session.close()
    return redirect(
        url_for('.learn', collId=collId, cardId=cardId, percent_done=percent_done, mode=request.args.get('mode')))


class Performance(Enum):
    again = 1
    good = 3
    easy = 5


class Cards:
    flashcardcollection = None
    new_card_ids = None
    to_review_ids = None
    current_place = 0
    collection_count = 0

    @staticmethod
    def init(collId):
        Cards.current_place = 0
        Cards.flashcardcollection_id = collId
        flashcardcollection = FlashcardCollection.query.get_or_404(collId)
        Cards.collection_count = len(flashcardcollection.flashcards.all())
        Cards.new_card_ids = flashcardcollection.get_new_card_ids()
        Cards.to_review_ids = flashcardcollection.get_reviewed_card_ids()

    @staticmethod
    def choose_next():
        if len(Cards.to_review_ids) > 0:
            percent_done = (Cards.current_place / Cards.collection_count) * 100
            Cards.current_place += 1
            p, c = math.ceil(percent_done), Cards.to_review_ids.pop()
            return p, c
        elif len(Cards.new_card_ids) > 0:
            percent_done = (Cards.current_place / Cards.collection_count) * 100
            Cards.current_place += 1
            p, c = math.ceil(percent_done), Cards.new_card_ids.pop()
            return p, c
        else:
            return 100, -1

    @staticmethod
    def reject_card(self, card):
        if card.is_new:
            self.new_cards.insert(0, card)
        else:
            self.to_review.insert(0, card)
