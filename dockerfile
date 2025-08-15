# start by pulling the python image
FROM python:3.8-alpine

# copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt

# switch working directory
WORKDIR /app

RUN python3 -m pip install --upgrade pip
RUN apk update && apk add python3-dev \
                        gcc \
                        libc-dev libffi-dev openssh gcc musl-dev
#RUN pip install cython
# install the dependencies and packages in the requirements file
RUN pip install -r requirements.txt

#RUN apk del .build-deps gcc musl-dev
# copy every content from the local file to the image
COPY app/*.* /app/

#RUN ssh-keygen -t rsa -f /root/.ssh/id_rsa -N ""
#RUN cp /root/.ssh/id_rsa.pub /app

# configure the container to run in an executed manner
ENTRYPOINT [ "python" ]

CMD ["-u","/app/main.py" ]
