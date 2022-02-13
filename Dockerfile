FROM public.ecr.aws/lambda/python:3.7

# copy function code and models into /var/task
COPY ./ ${LAMBDA_TASK_ROOT}/

RUN yum -y install gcc
RUN python3 -m pip install -r requirements.txt --target ${LAMBDA_TASK_ROOT}
RUN rm -r dataclasses*

# This is the entrypoint
CMD [ "handler.forecast"]
