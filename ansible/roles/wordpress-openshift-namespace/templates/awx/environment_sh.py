DATABASE_USER={{ awx_postgresql_database['user'] }}
DATABASE_NAME={{ awx_postgresql_database['name'] }}
DATABASE_HOST={{ awx_postgresql_database['host'] }}
DATABASE_PORT={{ awx_postgresql_database['port'] }}
DATABASE_PASSWORD={{ awx_postgresql_database['password'] | eyaml(eyaml_keys) | trim_lines | b64encode }}
MEMCACHED_HOST=localhost
RABBITMQ_HOST=localhost
AWX_ADMIN_USER=awx-poc-admin
AWX_ADMIN_PASSWORD={{ awx_admin_passwords[openshift_namespace] | eyaml(eyaml_keys) | trim_lines | b64encode }}
