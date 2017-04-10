# from flask.ext.login import *
#
# class User(UserMixin):
#     pass
#
# @login_manager.user_loader
# def user_loader(email):
#     if email not in users:
#         return
#
#     user = User()
#     user.id = email
#     return user
#
#
# @login_manager.request_loader
# def request_loader(request):
#     email = request.form.get('email')
#     if email not in users:
#         return
#
#     user = User()
#     user.id = email
#
#     # DO NOT ever store passwords in plaintext and always compare password
#     # hashes using constant-time comparison!
#     user.is_authenticated = request.form['pw'] == users[email]['pw']
#
#     return user