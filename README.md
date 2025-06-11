# demo-atom-space


az login --use-device-code

az account show

az acr login --name maxregistry

az aks get-credentials --resource-group atom-max --name atom-max-training

kubectl config use-context atom-max-training

kubectl get all --all-namespaces
kubectl apply -f guestbook_namespace.yaml
kubectl apply -f guestbook-ui-deployment.yaml
kubectl apply -f guestbook-ui-svc.yaml
kubectl get all --all-namespaces

kubectl get deployments -n guestbook  
kubectl get services -n guestbook  
kubectl get configmaps -n guestbook 

docker tag tpaperorders:latest maxregistry.azurecr.io/tpaperorders:v3
docker images
docker push maxregistry.azurecr.io/tpaperorders:v3
kubectl apply -f aks_tpaperorders-deploy.yaml
kubectl get all --all-namespaces

docker tag tpaperdelivery:latest maxregistry.azurecr.io/tpaperdelivery:v1
docker images
docker push maxregistry.azurecr.io/tpaperdelivery:v1
kubectl apply -f aks_tpaperdelivery-deploy.yaml
kubectl get all --all-namespaces

kubectl logs tpaperdelivery-599b8cd4b7-8nxzz daprd
kubectl logs tpaperdelivery-599b8cd4b7-8nxzz tpaperdelivery

---------------------------------------------------------------
```
kubectl apply -f namespace.yaml

kubectl apply -f backend-configmap.yaml

kubectl apply -f backend-secret.yaml

kubectl apply -f backend-deployment.yaml

kubectl apply -f frontend-deployment.yaml 

kubectl apply -f redis-deployment.yaml
```

```
kubectl get all -n devbcn
```

```
docker-compose up --build
docker-compose down
```

Port forwarding 

```
kubectl port-forward svc/backend -n devbcn 5000:5000 &
kubectl port-forward svc/frontend -n devbcn 8080:80 &
kubectl port-forward svc/redis -n devbcn 6379:6379 &
```

Kill tasks
```
taskkill /IM kubectl.exe /F
```



