#!/usr/bin/env python3

"""
Given an AWS Batch Compute Environment, find out which
jobs are running on which instances.
"""

import sys
import warnings

import boto3
import paramiko


def main():  # pylint: disable=too-many-locals
    "do the work"
    if len(sys.argv) != 2:
        print("please supply a compute environment name.")
        sys.exit(1)
    print("instance-id\tpublic-ip\tcontainer-name\tjob-id")
    comp_env = sys.argv[1]
    batch = boto3.client("batch")
    resp = batch.describe_compute_environments(computeEnvironments=[comp_env])
    cluster = resp["computeEnvironments"][0]["ecsClusterArn"]
    ecs = boto3.client("ecs")
    # TODO: paginate this:
    ecs_instances = ecs.list_container_instances(cluster=cluster)[
        "containerInstanceArns"
    ]
    instances = ecs.describe_container_instances(
        cluster=cluster, containerInstances=ecs_instances
    )["containerInstances"]
    instance_ids = [x["ec2InstanceId"] for x in instances]
    ec2 = boto3.client("ec2")
    # TODO paginate this:
    reservations = ec2.describe_instances(InstanceIds=instance_ids)["Reservations"]
    ec2_instances = []
    for reservation in reservations:
        ec2_instances.extend(reservation["Instances"])
    ipmap = {}
    for ec2_instance in ec2_instances:
        ipmap[ec2_instance["InstanceId"]] = ec2_instance["PublicIpAddress"]
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    for ec2_instance_id, ip_addr in ipmap.items():
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # TODO unhardcode/parameterize ssh key:
            ssh.connect(
                ip_addr,
                username="ec2-user",
                key_filename="/Users/dtenenba/.ssh/aws-batch.pem",
            )
        _, stdout, _ = ssh.exec_command(
            'sudo docker ps --format "{{.Names}}"|grep -v "ecs-agent"'
        )
        raw = stdout.read().decode("utf-8").strip()
        container_names = raw.split("\n")
        for container_name in container_names:
            _, stdout, _ = ssh.exec_command(
                "sudo docker exec {} env|grep AWS_BATCH_JOB_ID".format(container_name)
            )
            raw = stdout.read().decode("utf-8").strip()
            job_id = raw.split("=")[1]
            #    print("instance-id\tpublic-ip\tcontainer-name\tjob-id")
            print(
                "{}\t{}\t{}\t{}".format(
                    ec2_instance_id, ip_addr, container_name, job_id
                )
            )


if __name__ == "__main__":
    main()
