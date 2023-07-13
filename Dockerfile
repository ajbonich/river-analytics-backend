FROM public.ecr.aws/lambda/python:3.10

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt ${LAMBDA_TASK_ROOT}

COPY lambda_function.py ${LAMBDA_TASK_ROOT}

COPY app ${LAMBDA_TASK_ROOT}/app

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

CMD [ "lambda_function.handler" ]
#CMD [ "app.controllers.forecast_controller.get_forecast" ]
