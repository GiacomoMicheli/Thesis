#Starting from python 3.7 image
FROM python:3.8

#The /code directory becomes the default\starting directory
WORKDIR /code

#Load the requirements.txt file containing the python dependencies
COPY requirements.txt requirements.txt

#Install the python requirements
RUN pip3 install -r requirements.txt

#Copy all the files from the build context to the container
COPY . .

ENTRYPOINT [ "python3" ]

#Setup the default command
CMD ["app.py"]