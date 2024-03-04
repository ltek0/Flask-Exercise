from app import flask_app, db, forms
from app.models import Post
from app.routes_tools import get_next_url_from_request

from flask_login import current_user, login_required

from flask import render_template, redirect, url_for, flash, request, abort


@flask_app.route('/new_post', methods=['GET', 'POST'])
@login_required
def create_post():
    
    # redirect to login with message if not logged in
    if not current_user.is_authenticated:
        flash('You must be logged in to create a post')
        return redirect(url_for('login', next = url_for('create_post')))
    
    form  = forms.post.Create()
    if form.validate_on_submit():

        # specify new post data
        post_data = {
            'title': form.title.data,
            'body': form.body.data,
            'author': current_user
        } 
        post = Post(**post_data)
        
        # on sucess will be populated with id
        post = post.create()
        if post: # redirect to new post
            return redirect(url_for('view_post', post_id=post.id))
        
        else: # error
            flash('Post creation failed')
            return redirect(url_for('create_post'))

    # get request or form
    return render_template('post/create.html.j2', form=form, title='Create Post', current_user= current_user)


@flask_app.route('/p/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get(post_id)
    # post not found
    if not post:
        return abort(404)
    
    # post not owned by user
    elif post.author.id != current_user.id:
        return abort(404)
    
    # found, edit
    form = forms.post.Edit()
    if form.validate_on_submit():

        post.body = form.body.data
        post.update()

        return redirect(url_for('view_post', post_id=post.id))

    # populate form with post data
    elif request.method == 'GET':
        form.body.data = post.body

    # get request or form
    return render_template('post/edit.html.j2', form=form, title='Edit Post', post=post) 


@flask_app.route('/p/<int:post_id>')
def view_post(post_id: int):
    post = Post.query.get(post_id)
    if not post:
        return abort(404)
    else:
        return render_template('post/view.html.j2', post=post, title=post.title)
    

@flask_app.route('/p/<int:post_id>/delete')
@login_required
def delete_post(post_id: int):
    post = Post.query.get(post_id)
    if not post:
        return abort(404)
    elif post.author.id != current_user.id:
        return abort(404)
    else:
        db.session.delete(post)
        db.session.commit()
        return redirect(url_for('index'))