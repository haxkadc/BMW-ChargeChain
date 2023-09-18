#!/bin/bash
#
# SPDX-License-Identifier: Apache-2.0

rm $(pwd)/admin/wallet/appUser.id
rm $(pwd)/Client/wallet/appClient.id
cd "../test-network/"
./network.sh down

./network.sh up createChannel

./network.sh deployCC -ccn BMW

