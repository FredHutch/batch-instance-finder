# batch-instance-finder

Given the name of an AWS Batch Compute Environment, find out which 
Batch jobs are running on which EC2 instances. 

Outputs TSV-formatted output like the following:

```
instance-id	public-ip	container-name	job-id
i-0ad643479ef3cdd3e	52.36.245.12	ecs-isoseq3-polish-3-default-a2d7bd92ea9d928fec01	77dcc3bc-57b2-4451-a218-a78031a2a5a2:8
i-07896fd4bcf2d4501	34.214.180.24	ecs-isoseq3-polish-3-default-bab9cce9f595f5dbb101	77dcc3bc-57b2-4451-a218-a78031a2a5a2:1
```

## TODOS

There are some TODOS in the code which (when implemented)  will make it a bit more robust.


