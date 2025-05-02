ifeq ($(wildcard $(addsuffix /rm,$(subst :, ,$(PATH)))),)
	WINMODE := 1
else
	WINMODE := 0
endif

ifeq ($(WINMODE),1)
	DATE := $(shell powershell -Command "(Get-Date).ToString('yyyy-MM-dd')")
else
	DATE := $(shell date '+%Y-%m-%d')
endif

ifeq ($(strip $(filename)),)
	DUMP_FILE := /opt/dumps/$(DATE).gz
else
	DUMP_FILE := /opt/dumps/$(filename).gz
endif

dump:
	docker compose exec postgres sh -c 'pg_dump -U medialibrary -d medialibrary -h localhost -Fc | gzip > $(DUMP_FILE)'

load:
	docker compose stop django
	docker compose exec postgres dropdb medialibrary -U medialibrary
	docker compose exec postgres createdb medialibrary -U medialibrary
	docker compose exec postgres sh -c 'gunzip -c $(DUMP_FILE) | pg_restore -U medialibrary -d medialibrary'
	docker compose start django

create_data:
	docker compose exec django python scripts/create_data.py
