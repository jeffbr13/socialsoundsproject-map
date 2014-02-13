MONGO_PATH='/tmp/db'

mkdir -p $MONGO_PATH
chown `id -u` $MONGO_PATH
mongod --dbpath $MONGO_PATH
