# Step 3. Application deployment, templating, first issues

- **Hands-on:** Create a reusable base manifest for your application (deployment/service).
- **Hands-on:** Implement environment-specific envs for "test" and "prod":
    - Modify replica counts, resource limits, environment variables.
    - Inject environment-specific configuration (via ConfigMaps or Secret references).
- Deploy via Argo CD and verify environment-specific deployment.
- To run commands here please switch to infra root, where you see subfolder argo-cd

So far we have setup only Argo and its configuration structure, while working from a local machine, now is the time to work with applications, we will start with the single front-end app.

### Repository structure evolution

We had a following folder structure in our infrastructure repository
```yaml
argo-cd/  
├── base/  
│   ├── install.yaml  
│   └── kustomization.yaml
└── envs/  
    └── dev/  
        ├── restrict-default-project.yaml  
        ├── argocd-cm-patch.yaml  
        ├── argocd-rbac-cm.yaml  
        ├── project-devbcn-demo.yaml  
        └── kustomization.yaml
```

Now it is evolving to the following structure. We are not touching best practices yet :)
```yaml
infrastructure-repo/  
├── apps/                                 # Kubernetes application manifests  
│   ├── common/  
│   │   ├── base/  
│   │   │   ├── namespace-devbcn.yaml     # Namespace definition for devbcn-demo  
│   │   │   └── kustomization.yaml  
│   │   └── envs/  
│   │       └── dev/  
│   │           └── kustomization.yaml    # Dev environment empty overlay  
│   │  
│   └── frontend/  
│       ├── base/  
│       │   ├── deployment.yaml           # Deployment frontend app  
│       │   ├── service.yaml              # Service frontend app  
│       │   └── kustomization.yaml  
│       └── envs/  
│           └── dev/  
│               ├── replicas-patch.yaml   # Replica count change for dev  
│               └── kustomization.yaml  
│  
├── argo-cd/                              # Argo CD installation and configuration manifests  
│   ├── base/  
│   │   ├── install.yaml                  # Base Argo CD installation manifest  
│   │   └── kustomization.yaml  
│   └── envs/  
│       └── dev/  
│           ├── argocd-cm-patch.yaml          # User creation devbcn-user  
│           ├── argocd-rbac-cm-patch.yaml     # RBAC for new project+user  
│           ├── kustomization.yaml  
│           ├── project-devbcn-demo.yaml      # Definition of Argo CD project for devbcn-demo  
│           └── restrict-default-project.yaml # Restrict default project access  
│  
└── argo-cd-apps/                        # Argo CD Application CRDs pointing to apps  
    ├── common/  
    │   └── base/  
    │       └── common-app.yaml          # manifest for common resources  
    └── frontend/  
        └── frontend-application.yaml    # manifest for frontend app  
```

### Application manifests folder

Folder “Common” contains manifests for deployment of a namespace where shared Kubernetes resources will be deployed

### Common folder with namespace manifest

**namespace-devbcn.yaml**
```yaml
# root/apps/common/base/namespace-devbcn.yaml 
apiVersion: v1  
kind: Namespace  
metadata:  
  name: devbcn
```

**kustomization.yaml**
```yaml
# root/apps/common/base/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1  
kind: Kustomization  
  
resources:  
  - namespace-devbcn.yaml 
```

Validate changes with command below, assuming that terminal is at root folder
```yaml
kustomize build apps/common/base/
```

* We ignoring dev specific overlay and leaving it empty

### Frontend app folder

Base subfolder:

**deployment.yaml**
```yaml
# root/apps/frontend/base/deployment.yaml
apiVersion: apps/v1  
kind: Deployment  
metadata:  
  name: frontend  
  namespace: devbcn-demo
spec:  
  replicas: 1  
  selector:  
    matchLabels:  
      app: frontend  
  template:  
    metadata:  
      labels:  
        app: frontend  
    spec:  
      containers:  
        - name: frontend  
          image: docker.io/stasiko/funneverends-frontend:latest  
          ports:  
            - containerPort: 80  
```

**service.yaml**
```yaml
# root/apps/frontend/base/service.yaml
apiVersion: v1  
kind: Service  
metadata:  
  name: frontend  
  namespace: devbcn-demo  
spec:  
  selector:  
    app: frontend  
  type: ClusterIP # Change to LoadBalancer if you need external exposure  
  ports:  
    - port: 80  
      targetPort: 80  
```

**kustomization.yaml**
```yaml
# root/apps/frontend/base/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1  
kind: Kustomization  
  
resources:  
  - deployment.yaml  
  - service.yaml  
```

Dev overlays folder envs\dev

**deployment-patch.yaml** with changed replicas count
```yaml
# apps/frontend/envs/dev/deployment-patch.yaml
apiVersion: apps/v1  
kind: Deployment  
metadata:  
  name: frontend  
  namespace: devbcn-demo 
spec:  
  replicas: 2  
```

**kustomization.yaml**
```yaml
# apps/frontend/envs/dev/kustomization.yaml 
apiVersion: kustomize.config.k8s.io/v1beta1  
kind: Kustomization  
  
resources:  
  - ../../base  
  
patches:  
- path: deployment-patch.yaml 
```

Validate changes with 
```yaml
kustomize build apps/frontend/envs/dev/
```

As you know, kustomize is a part of kubectl, so command below will also work. We separating them for clear separation by workshop participants
```yaml
kubectl kustomize apps/frontend/envs/dev/
```

## Argo CD application manifests (CRDs)

Argo CD Applications are special Kubernetes resources (called Custom Resources)

There will be simpler structure here, because Argo recommends less usage of Kustomize, because things can be messier this way :)

Lets navigate to: argo-cd-apps/common

**common-app.yaml**
```yaml
# argo-cd-apps/common/common-app.yaml 
apiVersion: argoproj.io/v1alpha1  
kind: Application  
metadata:  
  name: common-resources  
  namespace: argocd  
  annotations:  
    argocd.argoproj.io/sync-wave: "0" 
spec:  
  project: common-resources  
  source:  
    repoURL: https://github.com/staslebedenko/dev-infrastructure.git  # Change to your Repo URL  
    targetRevision: HEAD  
    path: apps\common\base                # path to app manifest  
  destination:  
    server: https://kubernetes.default.svc  
    namespace: default               # For namespaces use "default"
  syncPolicy:  
    automated:  
      prune: false                   # the destination resource will not be deleted  
      selfHeal: true  
```

then argo-cd-apps/frontend

**frontend-application.yaml**
```yaml
# argo-cd-apps/frontend/frontend-application.yaml
apiVersion: argoproj.io/v1alpha1  
kind: Application  
metadata:  
  name: frontend-test  
  namespace: argocd  
  annotations:  
    argocd.argoproj.io/sync-wave: "1" 
spec:  
  project: devbcn-demo  
  source:  
    repoURL: https://github.com/staslebedenko/dev-infrastructure.git  
    targetRevision: HEAD  
    path: apps/frontend/envs/dev  
  destination:  
    server: https://kubernetes.default.svc  
    namespace: devbcn  
  syncPolicy:  
    automated:  
      prune: true  
      selfHeal: true  
```

Argo CD sync waves allow you to orchestrate the deployment order of Kubernetes resources by adding annotations ([argocd.argoproj.io/sync-wave](http://argocd.argoproj.io/sync-wave)) to your manifests. Resources with lower sync-wave numbers (e.g., "0") are synchronized first, and only after they are successfully deployed does Argo CD proceed to resources with higher wave numbers (e.g., "1", "2", etc.). This helps manage dependencies clearly, ensuring critical resources—such as namespaces, CRDs, or other prerequisites—are deployed successfully before the applications or services relying on them begin deployment, thus providing safer and more controlled rollouts.

## Deployment fun

Now we will try to deploy our applications and fix some errors along the way.

First - please commit all files above to git repo and push it to your public github repo.  

Please do the switch context to your cluster, to avoid problems :)
```yaml
kubectl config use-context devbcn-cluster
kubectl get ns
```

Check if Argo is accessible via [localhost:8080](http://localhost:8080) - if not, restart port forwarding below
```yaml
$job = Start-Job -ScriptBlock { kubectl port-forward svc/argocd-server -n argocd 8080:443 }
```

Then proceed with manual deployment of namespace and frontend app from the root. 
We will automate this during the next step of workshop with App of Apps pattern.

```yaml
kubectl apply -n argocd -f argo-cd-apps/common/common-app.yaml 
kubectl apply -n argocd -f argo-cd-apps/frontend/frontend-application.yaml
```

Now we have a following status

![image.png](attachment:5c5e1b34-97bc-46f6-b026-18b3db45bf08:image.png)

As you can see, deployment of common-resources app failed, but Argo showing it as healthy - why?

- Argo CD's "Health" status tracks the health of Kubernetes resources that **already exist**.
- If no Kubernetes resources are created yet (due to manifest-rendering errors), Argo CD has no resource statuses to report as unhealthy.
- Manifest-rendering issues (like missing paths or repository errors) affect **Sync Status**, not the Health Status.

![image.png](attachment:c0966082-2440-44c5-a865-6de66b11790f:image.png)

![image.png](attachment:8e28616c-b4bd-4de4-979a-74fcddd3763c:image.png)

But before fixing this issue, lets have a look at Frontend. With waves approach sync should not be started, or is it?

- If Wave `0` manifests **fail to render** (due to incorrect paths or invalid manifests), Argo CD will NOT create those resources at all, and the sync will show a `ComparisonError`.
- Because Wave `0` resources are never successfully synced (not created), Argo CD will **not proceed** to deploy Wave `1`.However, if Wave `0` has no resources at all (for example, due to a manifest rendering issue, Argo CD sees nothing to deploy), it may skip directly to Wave `1`. This can be confusing.
- If Wave `0` is empty (no resources created at all due to manifest errors), Argo CD treat that wave as trivially complete and proceed to Wave `1`.
- If Wave `0` has resources defined but fails due to **Kubernetes errors at apply-time** (e.g., validation errors, admission controllers, etc.), Argo CD stops and won't proceed to the next waves.

Now we know that path inside manifest is wrong, lets fix it in UI.

Click DETAILS, MANIFEST, EDIT

![image.png](attachment:6d56e2df-95fc-4521-a702-7bb4cc42f842:image.png)

![image.png](attachment:15a635e7-3ba5-4065-ba00-6e0c95187e4e:image.png)

And change  apps\common\base to  apps/common/base
Click SAVE and click to EVENTS to see that Sync operation succeeded. 

! But that is not the end of this story, if you will check your github repository, it still contains manifest with error above, Argo CD don’t merge back changes done in the UI and it is a classic configuration drift after ClickOps activity. Next time you deploy or Argo sync this Common resources CRD manifest application will be broken again. Never ever do anything in the UI :).

! Another bad thing that happen with this manifest is part below, argo project that was auto created from common-resources manifest. It was not configured with project manifest in argo-cd folder, please add it and apply to cluster like project-devbcn-demo.yaml, but make it available for every namespace and deploy with kubectl or kustomize

```yaml
# argo-cd/envs/dev/project-devbcn-demo.yaml
apiVersion: argoproj.io/v1alpha1  
kind: AppProject  
metadata:  
  name: devbcn-demo  
  namespace: argocd  
spec:  
  description: "Project for devbcn deployments"  
  sourceRepos:  
    - "*" # Allow all repositories, or specify your Git repos explicitly  
  destinations:  
    - namespace: devbcn-demo # Allow all namespaces, or restrict to specific namespaces if needed  'https://your.git.repo/applications.git'
      server: "*"    # Allow all clusters, or restrict to specific clusters  
  clusterResourceWhitelist:  
    - group: "*"  
      kind: "*"  
  namespaceResourceWhitelist:  
    - group: "*"  
      kind: "*"  
```

Now we have a following

![image.png](attachment:66e31949-3c1e-4dbf-97f7-41ab2109fa64:image.png)

If you will check with command below, you will see that new namespace is available

```yaml
kubectl get namespaces
```

But sync status on frontend will be in a failed state

![image.png](attachment:4c08327c-ddd9-4756-985f-b7300bd704e6:image.png)

This is because default configuration setting for this app is Retry disabled

![image.png](attachment:3657a034-616e-466b-8190-83e63367f7ab:image.png)

We need to click SYNC and then SYNCHRONIZE

![image.png](attachment:44c5ca0a-c2bd-426c-9828-cfe80ac589ea:image.png)

Quick explanation of the UI

- **PRUNE**: Delete Kubernetes resources not defined in Git manifests.
- **DRY RUN**: Preview sync without applying changes.
- **APPLY ONLY**: Apply manifests without waiting for resource readiness.
- **FORCE**: Recreate resources forcibly if normal apply fails (destructive).
- **SKIP SCHEMA VALIDATION**: Skip validation of manifests against Kubernetes schemas.
- **AUTO-CREATE NAMESPACE**: Automatically create missing namespaces during sync.
- **PRUNE LAST**: Delete resources after successful deployment of new resources.
- **APPLY OUT OF SYNC ONLY**: Apply only resources that differ from Git.
- **RESPECT IGNORE DIFFERENCES**: Respect rules defined for ignoring certain manifest differences.
- **SERVER-SIDE APPLY**: Use Kubernetes Server-Side Apply feature.
- **REPLACE**: Use 'kubectl replace' instead of 'kubectl apply' (destructive, careful!).
- **RETRY**: Automatically retry sync if it fails initially.
- **PRUNE PROPAGATION POLICY**: Controls how dependent resources are deleted (foreground/background).

And now everything is green 

![image.png](attachment:cd16583a-09cf-4f97-b0ae-692d94942fdf:image.png)

## Exercises

### Failing of Frontend app sync - sad story

Lets edit kustomize.yaml and add namespace row set to devbcn
```yaml
# apps/frontend/envs/dev/kustomization.yaml 
apiVersion: kustomize.config.k8s.io/v1beta1  
kind: Kustomization  

namespace: devbcn

resources:  
  - ../../base  
  
patches:  
- path: deployment-patch.yaml 
```

Test if result manifest change to the new namespace with
```yaml
kustomize build apps/frontend/envs/dev/
```

One side note, that change of namespace only in deployment-patch.yaml will result in the following error

![image.png](attachment:8c4799de-e38e-4903-9edf-134e3cf1500d:image.png)

And commit back to our repository, to see that we now have a Sync failed

![image.png](attachment:662fdb34-da89-4176-9c01-2b376f965df1:image.png)

In theory, sync with enabled Auto-create namespace should solve the problem, but this will not help in our situation, even with more destructive sync options enabled

![image.png](attachment:8b645494-3d6b-43e8-a92d-c1dfd9917d09:image.png)

Another good thing that Argo keeping our app alive

![image.png](attachment:c450d456-7de7-4804-a3e3-075924d03bc6:image.png)

![image.png](attachment:4d3ce91c-f6c0-44c5-9e61-a6e069d08b3a:image.png)

Commit and run sync with auto namespace creation again

This will going to fail because we will require PRUNE to delete service from old namespace

## Auto healing

This is less fun

We will reverting changes of devbcnnamespace and ensuring that frontend application is green

Open ArgoCD UI, select Frontend, click DETAILS ⇒ SUMMARY ⇒ EDIT = SYNC POLICY and click on to the SELF HEAL - ENABLE. You will see button DISABLE after change. 

![image.png](attachment:b5ab3be3-5883-4703-b3d5-0904c9288807:image.png)

Then we will delete our Frontend service with kubectl command
```yaml
kubectl -n devbcn-demo delete deployment frontend
```

This will result in out of sync, and then auto repair will happen

![image.png](attachment:51553e5b-278a-40d5-86a9-09867a22a470:image.png)

With the diff showing below

![image.png](attachment:88bc2577-4827-45e9-8afd-a3d767894ead:image.png)

In a few minutes it would be fixed, default 

A few lessons learned now about Argo behavior and issue resolution.

Scenario with Waves  - backend app intoduction as wave 1 with broken manifest and wrong namespace, deletion of the frontend and adding again with wave 3, what is going to happen

admin/fakeadminpass 

devbcn-user / password1234

The next step is 
```yaml
taskkill /IM kubectl.exe /F
```

Lesson 1. Be consistent with structure, our allocation of base folder for deploying existing resource is a bad idea :)

Lesson 2. Complexity raises fast, be aware that we are working now still with one environment and single cluster.

- One Argo, one cluster - environments by namespaces
- One Argo, one cluster setup + 3 env clusters
- Argo per env, each env 2 clusters
- etc
