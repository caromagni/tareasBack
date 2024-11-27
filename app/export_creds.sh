export postgres_user=developer
export postgres_password=development
export postgres_base=psql.beta.hwc.pjm.gob.ar:5432/tareas
export AUDIENCE=tareas_main
export REALM=internals
export AUTH_URL=https://dev-auth.pjm.gob.ar/auth/
export MAX_ITEMS_PER_RESPONSE=500
#export CUSTOM_ENVS=$(sops -d customization/local.env.enc)


# export postgres_user=postgres
# export postgres_password=0d70CINJNcVgckpI
# export postgres_base=delightfully-beloved-pollock.data-1.use1.tembo.io/tareas
# export AUDIENCE=account
# export REALM=internals
# export AUTH_URL=https://dev-auth.pjm.gob.ar/auth/
# export MAX_ITEMS_PER_RESPONSE=500
# #export CUSTOM_ENVS=$(sops -d customization/local.env.enc)
export RABBITMQ_USER='app_expediente'
export RABBITMQ_PASSWORD='DfwC4i3EN9tYM8RyfjzQ'
export RABBITMQ_HOST='dev-amqp.infra.pjm.gob.ar'
export RABBITMQ_PORT=5672
export RABBITMQ_VHOST='expediente'