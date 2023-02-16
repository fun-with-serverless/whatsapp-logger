from aws_cdk import (
    Stack,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_iam as iam,
    aws_sns as sns,
    aws_efs as efs,
    RemovalPolicy,
    aws_events as eb,
    aws_sqs as sqs,
    aws_events_targets as events_targets,
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
        event_bus: eb.EventBus,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = self._create_vpc()
        sg = self._create_security_group(vpc)
        file_system = self._create_efs(sg=sg, vpc=vpc)
        sqs_target = self._define_eventbus_events(event_bus)
        self._create_ecs_cluster(
            lambda_url=lambda_url,
            whatsapp_messages=whatsapp_messages,
            qr_bucket=qr_bucket,
            vpc=vpc,
            sg=sg,
            file_system=file_system,
            sqs_target=sqs_target,
            event_bus=event_bus,
        )

    def _define_eventbus_events(self, event_bus: eb.EventBus) -> sqs.Queue:
        queue = sqs.Queue(self, "UpdteWhatsAppListener")

        eb.Rule(
            self,
            "LogoutEventRule",
            event_bus=event_bus,
            event_pattern={"detail_type": ["logout"], "source": ["admin"]},
            targets=[events_targets.SqsQueue(queue)],
        )
        return queue

    def _create_vpc(self) -> ec2.Vpc:
        nat_gateway_provider = ec2.NatProvider.instance(
            instance_type=ec2.InstanceType("t3.micro")
        )
        vpc = ec2.Vpc(self, "VPC", max_azs=1, nat_gateway_provider=nat_gateway_provider)
        if self.node.try_get_context("stage") == "prod":
            vpc = ec2.Vpc(self, "VPC", max_azs=1)

        return vpc

    def _create_ecs_cluster(
        self,
        lambda_url: str,
        whatsapp_messages: sns.Topic,
        qr_bucket: s3.Bucket,
        vpc: ec2.Vpc,
        sg: ec2.SecurityGroup,
        file_system: efs.FileSystem,
        sqs_target: sqs.Queue,
        event_bus: eb.EventBus,
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
                "WHATAPP_SNS_TOPIC_ARN": whatsapp_messages.topic_arn,
                "PERSISTANCE_STORAGE_MOUNT_POINT": EFS_MOUNT_POINT,
                "URL_IN_MAIL": lambda_url,
                "SQS_EVENT_URL": sqs_target.queue_url,
                "EVENTBRIDGE_ARN": event_bus.event_bus_arn,
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
        fargate_task_definition.add_to_task_role_policy(
            iam.PolicyStatement(
                actions=["sqs:ReceiveMessage", "sqs:DeleteMessage"],
                resources=[sqs_target.queue_arn],
            )
        )
        fargate_task_definition.add_to_task_role_policy(
            iam.PolicyStatement(
                actions=["events:PutEvents"],
                resources=[event_bus.event_bus_arn],
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
