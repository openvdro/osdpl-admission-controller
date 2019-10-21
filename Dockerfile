FROM python:3.7

RUN mkdir -p /osdpl-admission-controller
COPY . /osdpl-admission-controller
RUN useradd -u 1000 -g users -d $(pwd) oac && chown -R oac:users /osdpl-admission-controller
WORKDIR /osdpl-admission-controller
RUN python -m pip install -r requirements.txt
EXPOSE 443
USER oac
ENTRYPOINT ["uwsgi", "uwsgi.ini"]
