output "linux_web_app_name" {
  value = azurerm_linux_web_app.example.name
}

output "app_url" {
  value = "https://${azurerm_linux_web_app.example.default_hostname}"
}

output "last_image" {
  value = "${data.docker_image.last_applied.id}"
}
