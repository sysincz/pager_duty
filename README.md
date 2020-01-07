# pager_duty


# docker run
```
docker run --rm --network host -e API_KEY=<api_key> sysincz/pager_duty:latest --service_name <service_name> --service_description "Service Description" --service_template "template" --show_api
```

# python run
```
python create_service.py --api_key=<api_key> --service_name <service_name> --service_description "Service Description" --service_template "template" --show_api
```

or
```
export API_KEY=<api_key>
python create_service.py  --service_name <service_name> --service_description "Service Description" --service_template "template" --show_api
```

# make run
```
export API_KEY=<api_key>
make test-docker-run
```

# Help script
```
python create_service.py -h
usage: create_service.py [-h] [--api_key API_KEY] --service_name SERVICE_NAME
                         --service_description SERVICE_DESCRIPTION
                         --service_template SERVICE_TEMPLATE [-d] [-a]

Create service in PagerDuty

optional arguments:
  -h, --help            show this help message and exit
  --api_key API_KEY     ApiKey PagerDuty
  --service_name SERVICE_NAME
                        Service Name in PagerDuty
  --service_description SERVICE_DESCRIPTION
                        Short Description for service
  --service_template SERVICE_TEMPLATE
                        Template for service
  -d, --debug           Run in debug mode
  -a, --show_api        Show service api key
```