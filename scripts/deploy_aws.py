#!/usr/bin/env python
"""
AWS deployment script for MyShop e-commerce platform
This script automates deployment to AWS ECS with Fargate
"""

import os
import sys
import boto3
import json
import time
import subprocess
from pathlib import Path

class AWSDeployer:
    """Class to handle AWS deployment"""
    
    def __init__(self):
        self.region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
        self.ecs_client = boto3.client('ecs', region_name=self.region)
        self.ecr_client = boto3.client('ecr', region_name=self.region)
        self.elbv2_client = boto3.client('elbv2', region_name=self.region)
        self.ec2_client = boto3.client('ec2', region_name=self.region)
        self.iam_client = boto3.client('iam', region_name=self.region)
        self.logs_client = boto3.client('logs', region_name=self.region)
        
    def create_ecr_repository(self, repository_name):
        """Create ECR repository for Docker images"""
        try:
            response = self.ecr_client.create_repository(
                repositoryName=repository_name,
                imageScanningConfiguration={'scanOnPush': True}
            )
            repository_uri = response['repository']['repositoryUri']
            print(f"ECR repository created: {repository_uri}")
            return repository_uri
        except self.ecr_client.exceptions.RepositoryAlreadyExistsException:
            print(f"ECR repository {repository_name} already exists")
            response = self.ecr_client.describe_repositories(repositoryNames=[repository_name])
            return response['repositories'][0]['repositoryUri']
        except Exception as e:
            print(f"Error creating ECR repository: {str(e)}")
            return None
    
    def build_and_push_docker_image(self, repository_uri, tag='latest'):
        """Build and push Docker image to ECR"""
        try:
            # Get ECR login token
            response = self.ecr_client.get_authorization_token()
            auth_data = response['authorizationData'][0]
            auth_token = auth_data['authorizationToken']
            proxy_endpoint = auth_data['proxyEndpoint']
            
            # Login to ECR
            login_cmd = f"aws ecr get-login-password --region {self.region} | docker login --username AWS --password-stdin {proxy_endpoint}"
            result = subprocess.run(login_cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"ECR login failed: {result.stderr}")
                return False
            
            # Tag and push image
            image_tag = f"{repository_uri}:{tag}"
            
            # Build Docker image
            print("Building Docker image...")
            build_cmd = f"docker build -t {image_tag} ."
            result = subprocess.run(build_cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Docker build failed: {result.stderr}")
                return False
            
            # Push to ECR
            print("Pushing Docker image to ECR...")
            push_cmd = f"docker push {image_tag}"
            result = subprocess.run(push_cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Docker push failed: {result.stderr}")
                return False
            
            print(f"Image pushed successfully: {image_tag}")
            return True
        except Exception as e:
            print(f"Error building/pushing Docker image: {str(e)}")
            return False
    
    def create_task_definition(self, family_name, image_uri, container_port=8000):
        """Create ECS task definition"""
        try:
            # Define container definition
            container_definition = {
                'name': 'myshop-web',
                'image': image_uri,
                'portMappings': [
                    {
                        'containerPort': container_port,
                        'hostPort': container_port,
                        'protocol': 'tcp'
                    }
                ],
                'environment': [
                    {'name': 'DEBUG', 'value': '0'},
                    {'name': 'ALLOWED_HOSTS', 'value': os.environ.get('DOMAIN', 'yourdomain.com')},
                ],
                'secrets': [
                    # Add secrets from AWS Secrets Manager or SSM Parameter Store
                ],
                'logConfiguration': {
                    'logDriver': 'awslogs',
                    'options': {
                        'awslogs-group': f'/ecs/{family_name}',
                        'awslogs-region': self.region,
                        'awslogs-stream-prefix': 'ecs'
                    }
                },
                'essential': True
            }
            
            # Register task definition
            response = self.ecs_client.register_task_definition(
                family=family_name,
                taskRoleArn=os.environ.get('TASK_ROLE_ARN', ''),
                executionRoleArn=os.environ.get('EXECUTION_ROLE_ARN', ''),
                networkMode='awsvpc',
                containerDefinitions=[container_definition],
                requiresCompatibilities=['FARGATE'],
                cpu='256',
                memory='512'
            )
            
            print(f"Task definition created: {response['taskDefinition']['taskDefinitionArn']}")
            return response['taskDefinition']['taskDefinitionArn']
        except Exception as e:
            print(f"Error creating task definition: {str(e)}")
            return None
    
    def create_cluster(self, cluster_name):
        """Create ECS cluster"""
        try:
            response = self.ecs_client.create_cluster(clusterName=cluster_name)
            print(f"Cluster created: {response['cluster']['clusterArn']}")
            return response['cluster']['clusterArn']
        except self.ecs_client.exceptions.ClusterAlreadyExistsException:
            print(f"Cluster {cluster_name} already exists")
            response = self.ecs_client.describe_clusters(clusters=[cluster_name])
            return response['clusters'][0]['clusterArn']
        except Exception as e:
            print(f"Error creating cluster: {str(e)}")
            return None
    
    def create_log_group(self, log_group_name):
        """Create CloudWatch log group"""
        try:
            self.logs_client.create_log_group(logGroupName=log_group_name)
            print(f"Log group created: {log_group_name}")
            return True
        except self.logs_client.exceptions.ResourceAlreadyExistsException:
            print(f"Log group {log_group_name} already exists")
            return True
        except Exception as e:
            print(f"Error creating log group: {str(e)}")
            return False
    
    def setup_load_balancer(self, lb_name, vpc_id, subnets):
        """Setup Application Load Balancer"""
        try:
            # Create target group
            tg_response = self.elbv2_client.create_target_group(
                Name=f"{lb_name}-tg",
                Protocol='HTTP',
                Port=8000,
                VpcId=vpc_id,
                HealthCheckPath='/health/',
                HealthCheckProtocol='HTTP',
                TargetType='ip'
            )
            target_group_arn = tg_response['TargetGroups'][0]['TargetGroupArn']
            print(f"Target group created: {target_group_arn}")
            
            # Create load balancer
            lb_response = self.elbv2_client.create_load_balancer(
                Name=lb_name,
                Subnets=subnets,
                Scheme='internet-facing',
                Type='application',
                IpAddressType='ipv4'
            )
            lb_arn = lb_response['LoadBalancers'][0]['LoadBalancerArn']
            print(f"Load balancer created: {lb_arn}")
            
            # Create listener
            self.elbv2_client.create_listener(
                LoadBalancerArn=lb_arn,
                Protocol='HTTP',
                Port=80,
                DefaultActions=[
                    {
                        'Type': 'forward',
                        'TargetGroupArn': target_group_arn
                    }
                ]
            )
            print("Load balancer listener created")
            
            return lb_arn, target_group_arn
        except Exception as e:
            print(f"Error setting up load balancer: {str(e)}")
            return None, None
    
    def deploy_service(self, cluster_name, service_name, task_definition_arn, 
                      target_group_arn, subnets, security_groups):
        """Deploy ECS service"""
        try:
            response = self.ecs_client.create_service(
                cluster=cluster_name,
                serviceName=service_name,
                taskDefinition=task_definition_arn,
                loadBalancers=[
                    {
                        'targetGroupArn': target_group_arn,
                        'containerName': 'myshop-web',
                        'containerPort': 8000
                    }
                ],
                desiredCount=2,
                launchType='FARGATE',
                networkConfiguration={
                    'awsvpcConfiguration': {
                        'subnets': subnets,
                        'securityGroups': security_groups,
                        'assignPublicIp': 'ENABLED'
                    }
                },
                deploymentConfiguration={
                    'maximumPercent': 200,
                    'minimumHealthyPercent': 50
                }
            )
            
            service_arn = response['service']['serviceArn']
            print(f"Service deployed: {service_arn}")
            return service_arn
        except Exception as e:
            print(f"Error deploying service: {str(e)}")
            return None
    
    def run_deployment(self):
        """Run complete deployment process"""
        print("Starting AWS deployment...")
        
        # Configuration
        app_name = 'myshop'
        cluster_name = f"{app_name}-cluster"
        repository_name = app_name
        task_family = f"{app_name}-task"
        service_name = f"{app_name}-service"
        lb_name = f"{app_name}-lb"
        log_group_name = f"/ecs/{task_family}"
        
        # Step 1: Create ECR repository
        print("\n1. Creating ECR repository...")
        repository_uri = self.create_ecr_repository(repository_name)
        if not repository_uri:
            return False
        
        # Step 2: Build and push Docker image
        print("\n2. Building and pushing Docker image...")
        if not self.build_and_push_docker_image(repository_uri):
            return False
        
        # Step 3: Create ECS cluster
        print("\n3. Creating ECS cluster...")
        cluster_arn = self.create_cluster(cluster_name)
        if not cluster_arn:
            return False
        
        # Step 4: Create log group
        print("\n4. Creating CloudWatch log group...")
        if not self.create_log_group(log_group_name):
            return False
        
        # Step 5: Create task definition
        print("\n5. Creating task definition...")
        task_definition_arn = self.create_task_definition(task_family, repository_uri)
        if not task_definition_arn:
            return False
        
        # Note: The remaining steps would require VPC, subnet, and security group information
        # which would typically be provided as environment variables or configuration
        print("\nDeployment setup completed!")
        print("Note: Complete deployment requires VPC configuration.")
        print("Please set the following environment variables and run the full deployment:")
        print("- VPC_ID")
        print("- SUBNET_IDS (comma separated)")
        print("- SECURITY_GROUP_IDS (comma separated)")
        print("- TASK_ROLE_ARN")
        print("- EXECUTION_ROLE_ARN")
        
        return True

def main():
    """Main deployment function"""
    print("MyShop AWS Deployment")
    print("====================")
    
    # Check AWS credentials
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"AWS Account: {identity['Account']}")
        print(f"AWS User: {identity['UserId']}")
    except Exception as e:
        print(f"AWS credentials not configured: {str(e)}")
        print("Please configure AWS credentials using 'aws configure'")
        sys.exit(1)
    
    # Run deployment
    deployer = AWSDeployer()
    success = deployer.run_deployment()
    
    if success:
        print("\nDeployment completed successfully!")
        print("Next steps:")
        print("1. Configure VPC settings in environment variables")
        print("2. Run the complete deployment with VPC configuration")
        sys.exit(0)
    else:
        print("\nDeployment failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()