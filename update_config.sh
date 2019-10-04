#!/bin/bash

MIKROTIK_ID=$1
[ -z "$MIKROTIK_ID" ] && exit 1

CONFDIR=config/mikrotik$MIKROTIK_ID
mkdir -p $CONFDIR
if ! scp root@vpn.jlsystem.cz:/etc/easy-rsa/2.0/keys/{ca.crt,mikrotik$MIKROTIK_ID.*} ./$CONFDIR/; then
	ssh root@vpn.jlsystem.cz "cd /etc/easy-rsa/2.0/; source vars; ./pkitool mikrotik$MIKROTIK_ID"
	scp root@vpn.jlsystem.cz:/etc/easy-rsa/2.0/keys/{ca.crt,mikrotik$MIKROTIK_ID.*} ./$CONFDIR/
fi
python mikrotik.py $MIKROTIK_ID > ./$CONFDIR/config.rsc

cat > ./$CONFDIR/deploy.sh << EOF
#!/bin/bash

IP=\$1
USERNAME=\$2
[ -z "\$IP" ] && exit 1
if [ -z "\$USERNAME" ]; then
	USERNAME=admin
fi

scp ca.crt mikrotik$MIKROTIK_ID.crt mikrotik$MIKROTIK_ID.key \$USERNAME@\$IP:
ssh \$USERNAME@\$IP "/certificate; import file-name=ca.crt passphrase=\"\"; import file-name=mikrotik$MIKROTIK_ID.crt passphrase=\"\";  import file-name=mikrotik$MIKROTIK_ID.key passphrase=\"\";"
cat config.rsc | ssh \$USERNAME@\$IP
EOF
