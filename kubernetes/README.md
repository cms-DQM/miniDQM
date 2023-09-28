# Kubernetes

Kubernetes manifest file can be found
in [minidqm.yaml](https://github.com/dmwm/CMSKubernetes/tree/master/kubernetes/cmsweb/services/minidqm.yaml). Deployment
is single pod with 2 containers for backend and frontend.

Deployment:

```shell
kubectl apply -f minidqm.yaml # will deploy services to dqm namespace
```

### Frontend container details

One workaround is to provide backend API base url to the frontend service in run time.

- We provide backend base url to `axios` so we don't define it in each axios request.
- It is provided in `frontend/src/main.js`
- We cannot use vite env variable feature of https://vitejs.dev/guide/env-and-mode.html because we build our service and
  run nginx.
- So, we use a custom solution after build to replace env variable `VITE_BACKEND_API_BASE_URL` with `sed`
  in `substitute_environment_variables.sh` before running `nginx`.

#### minidqm-secrets

It requires valid CERN user keytab to access /eos/cms

- Create keytab

```shell
# run ktutil command
ktutil

# it will give you an interactive prompt where you'll need to put your username
# and provide your password
addent -password -p $USER@CERN.CH -k 1 -e rc4-hmac
addent -password -p $USER@CERN.CH -k 1 -e aes256-cts
# Name of the file should be "keytab"
wkt keytab
quit
```

- Create `minidqm-secret` k8s secret in `-n dqm` namespace:

```kubectl -n dqm create secret generic minidqm-secrets --from-file=keytab --dry-run=client -o yaml | kubectl apply -f -```


