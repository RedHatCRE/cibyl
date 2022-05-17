OpenStack Plugin
================

OpenStack is an open source cloud software. The OpenStack plugin associates CI
job model with OpenStack deployment model.

Models
^^^^^^

* Deployment: An entire OpenStack cluster
* Node: A single node in an OpenStack deployment/cluster associated with a single deployment
* Container: A container associated with a single node
* Package: An RPM associated with either a single node or a single container
* Service: A service associated with a single deployment

::

    Deployment
    ├── Node
    │   └── Container
    │       └── Package
    │   └── Package
    ├── Service

Usage
^^^^^

To use the OpenStack plugin with Cibyl, specify `--plugin openstack`.

Arguments Matrix
----------------

.. list-table:: The supported arguments in the different built-in sources
   :widths: 20 40 10 10 10 10 10
   :header-rows: 1

   * - Argument / Source
     - Description
     - Jenkins
     - Zuul
     - ES
     - JJB
     - Zuul.d
   * - --ip-version
     - | The IP version used
       | by the deployment (4 or 6)
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
   * - --release
     - | OpenStack Release
       | (OSP and RDO supported)
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
   * - --infra-type
     - | The infrstructure on which
       | OS is deployed (e.g. ovb,
       | baremetal, virthost)
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
   * - --topology
     - | The combination of node
       | types deployed
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
   * - --controllers
     - | Number of controlllers
       | (Can be also range: ">=3")
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
   * - --computes
     - | Number of computes
       | (Can be also range: ">=3")
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
   * - --dvr
     - | Does the deployment use
       | Distributed Virtual Router
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
   * - --ml2-driver
     - | Which ml2 driver does
       | the deployment use
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
   * - --network-backend
     - | What network protocol is
       | used (e.g. vxlan, vlan, ...)
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
   * - --storage-backend
     - | What storage backend is
       | used (vlan, Ceph, Netapp)
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
   * - --tls-everywhere
     - | Does the deployment uses
       | TLS on all hosts
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:x:|
     - |:x:|
   * - --containers
     - | List of containers running
       | on the hosts
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:x:|
     - |:x:|
   * - --packages
     - | Package installed by the
       | deployment
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:x:|
     - |:x:|
   * - --services
     - | Services installed by the
       | deployment
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:x:|
     - |:x:|
