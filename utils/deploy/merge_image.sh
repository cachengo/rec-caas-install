#!/bin/bash
# Copyright 2019 Nokia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

source /etc/profile

CONC_MAX=4

conc() {
    local procs=(`jobs -p`)
    local proc_count=${#procs[*]}

    # Block until there is an open slot
    if ((proc_count >= CONC_MAX)); then
        wait ${procs[0]}
    fi

    # Start our task
    (eval "$@") &
}

merge() {
    TEMP=`getopt -o f:t:i: --long from-registry:,to-registry:,image-name: -- "$@"`
    eval set -- "$TEMP"

    while [ -n "$1" ]
    do
      case "$1" in
        -f|--from-registry) from_registry=$2; shift 2;;
        -t|--to-registry) to_registry=$2; shift 2;;
        -i|--image-name) image_name=$2; shift 2;;
        --) break ;;
        *) echo $1,$2,$show_usage; break ;;
      esac
    done

    d=`date`
    echo "---$d: Merge $image_name from $from_registry to $to_registry"

    # Get new image tag
    image_tag=`curl --cert /etc/docker-update-registry/update-registry.pem --key /etc/docker-update-registry/update-registry-key.pem --cacert /etc/docker-update-registry/ca.pem https://$from_registry/v2/$image_name/tags/list | awk -F'[' '{print $2}' | awk -F'"' '{print $2}'`

    echo "New image tag: $image_tag"

    # Check whether the image exists in the internal registry
    ret_existing_image_tags=`curl --cert /etc/docker-registry/registry1.pem --key /etc/docker-registry/registry1-key.pem --cacert /etc/docker-registry/ca.pem https://$to_registry/v2/$image_name/tags/list`

    ret_key=`echo $ret_existing_image_tags | awk -F'"' '{print $2}'`
    if [  $ret_key != "errors" ]; then
      existing_image_tags=`echo $ret_existing_image_tags | awk -F'[' '{print $2}' | awk -F']' '{print $1}' | sed "s/\"//g"`
      IFS=',' read -r -a existing_image_tag_list <<< "$existing_image_tags"
      for existing_tag in ${existing_image_tag_list[@]}; do
        if [ $existing_tag = $image_tag ]; then
          echo "The image exists in registry. Skip."
          exit 0
        fi
      done
    fi

    d=`date`
    echo "---$d: Start to pull image"
    docker pull $from_registry/$image_name:$image_tag
    docker tag $from_registry/$image_name:$image_tag $to_registry/$image_name:$image_tag

    d=`date`
    echo "---$d: Start to push image"
    docker push $to_registry/$image_name:$image_tag

    d=`date`
    echo "---$d: Start to clean local image"
    docker rmi $from_registry/$image_name:$image_tag
    docker rmi $to_registry/$image_name:$image_tag

    d=`date`
    echo "---$d: End merging"
}

IMGLIST=`sed "s/repositories:/""/g" <<< $3`
IMGLIST=`sed "s/{/""/g" <<< $IMGLIST`
IMGLIST=`sed "s/}/""/g" <<< $IMGLIST`
IMGLIST=`sed "s/\[/""/g" <<< $IMGLIST`
IMGLIST=`sed "s/\]/""/g" <<< $IMGLIST`
IMGLIST=`sed "s/\,/ /g" <<< $IMGLIST`

for a in $IMGLIST; do conc "merge $1 $2 --image-name=$a";done;wait;
