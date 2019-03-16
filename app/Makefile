test:
	pep8 --exclude=env,migrations --max-line-length=120 .
	python ./manage.py test --settings=zosia16.settings.test


deps: static/script/room.js
	yarn build

.PHONY: test deps
