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
    Duration,
)
from constructs import Construct

EFS_MOUNT_POINT = "/mnt/efs"


class WhatsAppListener(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        whatsapp_messages: sns.Topic,
        qr_bucket: s3.Bucket,
        lambda_url: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        email_identity = self._create_email_identity()

        vpc = ec2.Vpc(self, "VPC", max_azs=1)
        sg = self._create_security_group(vpc)
        file_system = self._create_efs(sg=sg, vpc=vpc)
        self._create_ecs_cluster(
            lambda_url=lambda_url,
            whatsapp_messages=whatsapp_messages,
            email_identity=email_identity,
            qr_bucket=qr_bucket,
            vpc=vpc,
            sg=sg,
            file_system=file_system,
        )

    def _create_ecs_cluster(
        self,
        lambda_url: str,
        whatsapp_messages: sns.Topic,
        email_identity: str,
        qr_bucket: s3.Bucket,
        vpc: ec2.Vpc,
        sg: ec2.SecurityGroup,
        file_system: efs.FileSystem,
    ) -> None:
        cluster = ecs.Cluster(self, "Cluster", vpc=vpc)
        fargate_task_definition = ecs.FargateTaskDefinition(
            self, "TaskDef", memory_limit_mib=1024, cpu=512
        )
        whatsapp_listener_container = fargate_task_definition.add_container(
            "Container",
            image=ecs.ContainerImage.from_asset("../whatsapp-web-listener"),
            environment={
                "QR_BUCKET_NAME": qr_bucket.bucket_name,
                "SEND_QR_TO": email_identity,
                "WHATAPP_SNS_TOPIC_ARN": whatsapp_messages.topic_arn,
                "PERSISTANCE_STORAGE_MOUNT_POINT": EFS_MOUNT_POINT,
                "URL_IN_MAIL": lambda_url,
            },
            logging=ecs.LogDrivers.aws_logs(stream_prefix="whatsapp-listener"),
        )
        fargate_task_definition.add_to_task_role_policy(
            iam.PolicyStatement(actions=["ses:SendEmail"], resources=["*"])
        )
        fargate_task_definition.add_to_task_role_policy(
            iam.PolicyStatement(
                actions=["sns:Publish"], resources=[whatsapp_messages.topic_arn]
            )
        )
        fargate_task_definition.add_to_task_role_policy(
            iam.PolicyStatement(
                actions=["s3:PutObject"], resources=[f"{qr_bucket.bucket_arn}/*"]
            )
        )

        efs_configuration = ecs.EfsVolumeConfiguration(
            file_system_id=file_system.file_system_id
        )
        fargate_task_definition.add_volume(
            name="whatsappListenerVolume", efs_volume_configuration=efs_configuration
        )
        whatsapp_listener_container.add_mount_points(
            ecs.MountPoint(
                container_path=EFS_MOUNT_POINT,
                source_volume="whatsappListenerVolume",
                read_only=False,
            )
        )
        ecs.FargateService(
            self,
            "Service",
            cluster=cluster,
            task_definition=fargate_task_definition,
            security_groups=[sg],
        )

    def _create_efs(self, vpc: ec2.Vpc, sg: ec2.SecurityGroup) -> efs.FileSystem:
        private_subnet = vpc.select_subnets(one_per_az=True).subnets[0]
        return efs.FileSystem(
            self,
            "FileSystem",
            vpc=vpc,
            removal_policy=RemovalPolicy.DESTROY,
            security_group=sg,
            vpc_subnets=ec2.SubnetSelection(subnets=[private_subnet]),
        )

    def _create_email_identity(self) -> str:
        email_identity = self.node.try_get_context("email_identity")
        if email_identity is None:
            raise Exception("Missing email_identity parameter")

        ses.EmailIdentity(
            self, "QRCodeIdentity", identity=ses.Identity.email(email_identity)
        )
        
        return email_identity

    def _create_security_group(self, vpc: ec2.Vpc) -> ec2.SecurityGroup:
        sg = ec2.SecurityGroup(self, "HTTPSOnly", vpc=vpc, allow_all_outbound=False)

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

        return sg
