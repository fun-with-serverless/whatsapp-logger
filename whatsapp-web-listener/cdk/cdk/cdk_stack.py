from aws_cdk import (
    Stack,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_iam as iam,
)
from constructs import Construct

class CdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        bucket = s3.Bucket(self, "QRImage")
        
        cluster = ecs.Cluster(self, "Cluster")
        
        sg = ec2.SecurityGroup(self, "HTTPSOnly", vpc=cluster.vpc, allow_all_outbound=False)

        sg.add_egress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(443),
        )
        
        fargate_task_definition = ecs.FargateTaskDefinition(self, "TaskDef", memory_limit_mib=512, cpu=256)
        fargate_task_definition.add_container("Container", image=ecs.ContainerImage.from_asset('../service'), environment={"QR_BUCKET_NAME":bucket.bucket_name}, logging=ecs.LogDrivers.aws_logs(stream_prefix="whatsapp-listener"))
        fargate_task_definition.add_to_task_role_policy(iam.PolicyStatement(actions=["s3:PutObject"], resources=[bucket.bucket_arn]))
        ecs.FargateService(self, "Service", cluster=cluster, task_definition=fargate_task_definition, security_groups=[sg])

