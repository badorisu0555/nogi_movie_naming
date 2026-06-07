import boto3

def update_ecs_service():
    client = boto3.client('ecs', region_name='ap-northeast-1')

    cluster_name = "ai_news"
    service_name = "ai_news-service"

    print(f"Updating service {service_name} in cluster {cluster_name}...")

    try:
        # ここを修正: force_new_deployment -> forceNewDeployment
        response = client.update_service(
            cluster=cluster_name,
            service=service_name,
            forceNewDeployment=True
        )
        
        print("Success! A new deployment has been forced.")
        # ステータス確認（PRIMARYが新しいデプロイ、ACTIVEが古いデプロイを指します）
        print("Deployments in progress...")
        for dep in response['service']['deployments']:
            print(f"- Status: {dep['status']}, Rollout: {dep['rolloutState']}")

    except Exception as e:
        print(f"Error updating service: {e}")

if __name__ == "__main__":
    update_ecs_service()