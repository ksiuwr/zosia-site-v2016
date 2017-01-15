test:
	pep8 --exclude=env,migrations --max-line-length=120 .
	python ./manage.py test --settings=zosia16.settings.test


deps: static/bower.json static/script/room.js
	npm run deps
	npm run build

.PHONY: test deps
