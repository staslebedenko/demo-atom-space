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

docker tag tpaperorders:latest maxregistry.azurecr.io/tpaperorders:v1
docker images
docker push maxregistry.azurecr.io/tpaperorders:v1
kubectl apply -f aks_tpaperorders-deploy.yaml
kubectl get all --all-namespaces

docker tag tpaperdelivery:latest maxregistry.azurecr.io/tpaperdelivery:v1
docker images
docker push maxregistry.azurecr.io/tpaperdelivery:v1
kubectl apply -f aks_tpaperdelivery-deploy.yaml
kubectl get all --all-namespaces
