.PHONY: local

rs:
	python manage.py runserver
check:
	python manage.py check
migration:
	python manage.py makemigrations
migrate:
	python manage.py migrate
# handmatig pre-commit
lint:
	pre-commit run -a
# pip-tools commands
dev-compile:
	pip-compile reqs/dev.in
req-compile:
	pip-compile reqs/req.in
# django_extention commands
rs-ex:
	python manage.py runserver_plus --nopin
shell:
	python manage.py shell_plus
shell-ip:
	python manage.py shell_plus --ipython
models:
	python manage.py list_model_info
help-admin:
	python manage.py admin_generator my_app
url:
	python manage.py show_urls
coverage:
	pytest --cov=sandbox --migrations -n 2 --dist loadfile

# fcov == "fast coverage" by skipping migrations checking.
# // processes ( need + package pytest-xdist)
# Save that for CI.(here processes: N==4)
fcov:
	@echo "Running fast coverage check"
	@pytest --cov=sandbox -n 2 --dist loadfile -q
	# @pytest --cov=sandbox