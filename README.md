# Flask-Exercise

reference: https://www.youtube.com/playlist?list=PLtgJR0xD2TPeVeq6azvnKXYSeYHFzGaMi

# Babel command for creating translations

creating translations

```
pybabel extract -F babel.cfg -k lazy_gettext -o app/translations/messages.pot .
pybabel init -i app/translations/messages.pot -d app/translations -l zh
```

complie and updayte

```
pybabel compile -d app/translations
pybabel update -i app/translations/messages.pot -d app/translations

```
