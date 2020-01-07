BINARY=pager_duty
GITHUB_USERNAME=sysincz
DOCKER_RUN_OPTS ?= --network host -e API_KEY=${API_KEY}
DOCKER_RUN_ARG ?= --service_name service_name --service_description "Service Description" --service_template "template" --show_api
VERSION := $(shell git describe --tags 2>/dev/null)
ifeq "$(VERSION)" ""
VERSION := $(shell git rev-parse --short HEAD)
endif

docker: 
	docker build -t $(GITHUB_USERNAME)/$(BINARY):$(VERSION) .

test-docker-run: docker
	docker run --rm $(DOCKER_RUN_OPTS) $(GITHUB_USERNAME)/$(BINARY):$(VERSION) $(DOCKER_RUN_ARG)

docker-push: docker
	docker push $(GITHUB_USERNAME)/$(BINARY):$(VERSION)
