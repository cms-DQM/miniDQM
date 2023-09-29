# miniDQM

CMS PPD Physics Run Monitoring Using DQM

## What it is

miniDQM provides overlaying functionality for the histograms defined in [plots.yaml](backend/config/plots.yaml) using
ROOT THStack. Its difference is to be able to overlay 10s of runs of ERAs in single drawing. Source histograms are
fetched directly from DQM ROOT files and no operation are applied on the data itself other than changing line colors and
styles to differentiate in the overlays. You can select defined groups, ERAs and RUNs of them and compare them
intelligently:

- if multiple ERAs are selected, each ERA RUN color will be same but RUNs of same ERA will have different line style
- if one ERA is selected, line colors and styles will be different for each RUN.

## How it works

Like all systems, this service also has inputs and output: pretty Tailwind/Vue/JsROOT powered frontend page. Inputs are
defined [plots.yaml](backend/config/plots.yaml) specific and easy to understand format with DQM ROOT files in their EOS
storage. Our parser service [eos_grinder](backend/dqm_meta/eos_grinder.py) parses all ROOT files with required metadata
information and these metadata used to fetch required histograms from ROOT files. Someone might think that reading
hundreds of ROOT files, getting histograms from them and stacking them is expensive operation, right! Because of this,
ROOT files access is limited to only getting JSON data of histograms and close them. All the operations are based on
histogram JSON data and features of PYROOT and JSROOT in front-end. Additionally, there is an LRU cache of python
function tools to not keep same histogram of same ROOT file in cache. I can say that speed is not problem if its usage
increase over time. Another cache mechanism to store JSON representation of histograms can be implemented easily.

### Backend

Backend can be separated to its clients and backend server

##### - FastAPI

[FastAPI](https://fastapi.tiangolo.com/) is used as web server. It is asynchronous and heavily dependent on pydantic
classes that makes typless-ness hell of python more desirable. It has a few API endpoints, main endpoint is to just get
histograms. All communication between fron-back ends depend on JSON representation of histograms.

##### - DQM META

DQM META consists of two components : eos grinder and client. EOS grinder is parses DQM ROOT files for all RUNs and
creates a JSON file parsed data. To get all the ROOT files in a base EOS directory, special Linux `find` command run
with subprocess. In deployment, EOS grinder runs hourly to update metadata information. Its input is base DQM EOS
directory and output is JSON file contains metadata.

DQM meta store client is responsible to create pydantic metadata object and functionalities to reach metadata. It reads
JSON file output of EOS grinder and converts to pydantic object. Anything that is required like all ROOT files of
Run2023A era, or dataset of an ROOT file can be found in the DQM meta store client. Pydantic model class itself has most
of the functionality even though file name is models.

##### - PYROOT

PyROOT is used to fetch JSON data of histograms and overlay them. Main functionality is to read histogram JSON as
efficiently as possible. Second important functionality is to overlay histograms. JSROOT is also capable of
overlaying/stacking histograms using THStack. However, when the size of histograms considered, it made sense to do
creation of THSTack object from histograms and send THStack TCanvas to frontend. Frontend(JSROOT) only deals with
drawing JSON data with these features of backend.

### Docker images and Kubernetes

Docker images are auto build with GH actions, and pushed to CERN registry.
Kubernetes manifest file can be found
in [minidqm.yaml](https://github.com/dmwm/CMSKubernetes/tree/master/kubernetes/cmsweb/services/minidqm.yaml). Deployment
is single
pod with 2 containers for backend and frontend.

## Kubernetes

Kubernetes manifest file can be found
in [minidqm.yaml](https://github.com/dmwm/CMSKubernetes/tree/master/kubernetes/cmsweb/services/minidqm.yaml). Deployment
is single pod with 2 containers for backend and frontend.

Deployment:

```shell
kubectl apply -f minidqm.yaml # will deploy services to dqm namespace
```

##### - Frontend container details

One workaround is to provide backend API base url to the frontend service in run time.

- We provide backend base url to `axios` so we don't define it in each axios request.
- It is provided in `frontend/src/main.js`
- We cannot use vite env variable feature of https://vitejs.dev/guide/env-and-mode.html because we build our service and
  run nginx.
- So, we use a custom solution after build to replace env variable `VITE_BACKEND_API_BASE_URL` with `sed`
  in `substitute_environment_variables.sh` before running `nginx`.

#### - minidqm-secrets

It requires valid CERN user keytab to access /eos/cms

- Create keytab in lxplus: `cern-get-keytab --keytab keytab --user --login $cernusername`

- Create `minidqm-secret` k8s secret in `-n dqm` namespace:

```kubectl -n dqm create secret generic minidqm-secrets --from-file=keytab --dry-run=client -o yaml | kubectl -n dqm apply -f -```


