#!/bin/bash

function add_to_pwcache {
  _PASS="${1}"

  if [[ "${!_PASS}" == "" ]]; then
    echo "export ${_PASS}=$(openssl rand -hex 10)" >>"${PWCACHE}"
  else
    echo "export ${_PASS}=${!_PASS}" >>"${PWCACHE}"
  fi
}

PWCACHE="${1}"

echo -n >"${PWCACHE}"

for PASS in MYSQL_DATABASE_PASSWORD RABBIT_PASS KEYSTONE_DBPASS \
  DEMO_PASS ADMIN_PASS SERVICE_PASS ADMIN_TOKEN \
  GLANCE_DBPASS GLANCE_PASS \
  NOVA_DBPASS NOVA_PASS \
  DASH_DBPASS \
  CINDER_DBPASS CINDER_PASS \
  NEUTRON_DBPASS NEUTRON_PASS \
  HEAT_DBPASS HEAT_PASS \
  CEILOMETER_DBPASS CEILOMETER_PASS \
  TROVE_DBPASS TROVE_PASS \
  MIDONET_PASS \
  NEUTRON_METADATA_SHARED_SECRET \
  SWIFT_PASS
do
  add_to_pwcache "${PASS}"
done

exit 0

