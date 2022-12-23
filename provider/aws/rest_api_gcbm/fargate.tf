resource "aws_ecs_task_definition" "backend_gcbm_api_task" {
  family = "backend_gcbm_api_app_family"

  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"

  memory = "512"
  cpu    = "256"

  execution_role_arn = aws_iam_role.ecs_role.arn

  container_definitions = <<EOT
[
    {
        "name": "gcbm_api_app_container",
        "image": "<your_ecr_repo_url>:latest",
        "memory": 512,
        "essential": true,
        "portMappings": [
            {
                "containerPort": 8080,
                "hostPort": 8080
            }
        ]
    }
]
EOT
}

resource "aws_ecs_cluster" "backend_gcbm_api_cluster" {
  name = "backend_gcbm_api_cluster_gcbm_api_app"
}

resource "aws_ecs_service" "backend_gcbm_api_service" {
  name = "backend_gcbm_api_service"

  cluster         = aws_ecs_cluster.backend_gcbm_api_cluster.id
  task_definition = aws_ecs_task_definition.backend_gcbm_api_task.arn

  launch_type   = "FARGATE"
  desired_count = 1

  network_configuration {
    subnets          = ["${aws_subnet.public_a.id}", "${aws_subnet.public_b.id}"]
    security_groups  = ["${aws_security_group.security_group_gcbm_api_app.id}"]
    assign_public_ip = true
  }
}
