FROM public.ecr.aws/lambda/python:3.10

COPY requirements.txt .
RUN pip3 install --upgrade pip
RUN pip3 install --user -r requirements.txt

WORKDIR ${LAMBDA_TASK_ROOT}

COPY app ${LAMBDA_TASK_ROOT}/app

CMD [ "app.controllers.forecast_controller.get_forecast" ]
