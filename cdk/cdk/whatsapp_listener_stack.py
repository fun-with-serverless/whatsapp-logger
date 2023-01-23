from aws_cdk import (
    Stack,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_iam as iam,
    aws_sns as sns,
    aws_efs as efs,
    RemovalPolicy,
    aws_ses as ses,
    aws_s3 as s3,
    CfnOutput,
    Duration
)
from constructs import Construct

EFS_MOUNT_POINT = "/mnt/efs"

class WhatsAppListener(Stack):

    def __init__(self, scope: Construct, construct_id: str, whatsapp_messages:sns.Topic, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        bucket = s3.Bucket(self, "QRImage")

        email_identity = self.node.try_get_context("email_identity")
        if email_identity is None:
            raise Exception("Missing email_identity parameter")
            
        ses.EmailIdentity(self, "QRCodeIdentity",  identity=ses.Identity.email(email_identity))
        vpc = ec2.Vpc(self, "VPC", max_azs = 1)
        cluster = ecs.Cluster(self, "Cluster", vpc = vpc)
        
        sg = ec2.SecurityGroup(self, "HTTPSOnly", vpc=cluster.vpc, allow_all_outbound=False)

        sg.add_egress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(443),
        )
        
        # For EFS
        sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(2049),
        )
        
        sg.add_egress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(2049),
        )
        
        private_subnet = vpc.select_subnets(one_per_az=True).subnets[0]
        file_system = efs.FileSystem(self, "FileSystem", vpc=vpc, removal_policy=RemovalPolicy.DESTROY, security_group=sg, vpc_subnets=ec2.SubnetSelection(subnets=[private_subnet]))
        
        fargate_task_definition = ecs.FargateTaskDefinition(self, "TaskDef", memory_limit_mib=1024, cpu=512)
        whatsapp_listener_container = fargate_task_definition.add_container("Container", image=ecs.ContainerImage.from_asset('../whatsapp-web-listener'), environment={"QR_BUCKET_NAME":bucket.bucket_name, "SEND_QR_TO":email_identity, "WHATAPP_SNS_TOPIC_ARN": whatsapp_messages.topic_arn, "PERSISTANCE_STORAGE_MOUNT_POINT": EFS_MOUNT_POINT}, logging=ecs.LogDrivers.aws_logs(stream_prefix="whatsapp-listener"))
        fargate_task_definition.add_to_task_role_policy(iam.PolicyStatement(actions=["ses:SendEmail"], resources=["*"]))
        fargate_task_definition.add_to_task_role_policy(iam.PolicyStatement(actions=["sns:Publish"], resources=[whatsapp_messages.topic_arn]))
        fargate_task_definition.add_to_task_role_policy(iam.PolicyStatement(actions=["s3:PutObject"], resources=[f"{bucket.bucket_arn}/*"]))
        
        efs_configuration = ecs.EfsVolumeConfiguration(file_system_id=file_system.file_system_id)
        fargate_task_definition.add_volume(name="whatsappListenerVolume", efs_volume_configuration=efs_configuration)
        whatsapp_listener_container.add_mount_points(ecs.MountPoint(container_path=EFS_MOUNT_POINT, source_volume="whatsappListenerVolume", read_only = False))
        ecs.FargateService(self, "Service", cluster=cluster, task_definition=fargate_task_definition, security_groups=[sg])
        
        CfnOutput(self, "QRBucket", value=bucket.bucket_name)



