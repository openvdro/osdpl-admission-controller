Admission Controller for Kubernetes OpenStackDeployment
=======================================================

Should be run under uwsgi, for example:

`$ uwsgi uwsgi.ini`

As the service runs under HTTPS, you need to also provide server certificate
and key (named oac.crt and oac.key) by default. They can be generated for
example by using this script: https://github.com/alex-leonhardt/k8s-mutate-webhook/blob/master/ssl/ssl.sh
