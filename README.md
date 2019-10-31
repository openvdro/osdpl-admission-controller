Admission Controller for Kubernetes OpenStackDeployment
=======================================================

You can read more about admission controllers [here](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers).
To use this particular admission controller, you need to have
ValidatingAdmissionWebhook admission plugin enabled in Kubernetes API server.

Should be run under uwsgi, for example:

`$ uwsgi uwsgi.ini`

As the service runs under HTTPS, you need to also provide server certificate
and key (named oac.crt and oac.key) by default. They can be generated for
example by using this script: https://github.com/alex-leonhardt/k8s-mutate-webhook/blob/master/ssl/ssl.sh
