# Flask-Exercise

reference: https://www.youtube.com/playlist?list=PLtgJR0xD2TPeVeq6azvnKXYSeYHFzGaMi

# Babel command for creating translations

creating translations

```
pybabel extract -F babel.cfg -k lazy_gettext -o app/translations/messages.pot .
pybabel init -i app/translations/messages.pot -d app/translations -l zh
```

complie and update

```
pybabel compile -d app/translations
pybabel update -i app/translations/messages.pot -d app/translations

```

# Labs

7. Error Handeling
8. Followers
9. Home page posts pagination
10. email
11. bootstrap
12. date and times
13. lang translations

# Running the application in codespace
1. create .flaskenv
``` 
.flaskenv.template to .flaskenv
change config as needed
contents in .template is set up for development in codespace and devcontainer
```
2. comple babel translations, see above documentation for details
3. run app.py or data_init.py to initialise the database\
All existing data in the database specified will be deleted and 5 users with 5 posts will be created for each users
4.

