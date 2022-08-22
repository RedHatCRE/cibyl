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

To use the OpenStack plugin with Cibyl, specify `--plugin openstack` or include it in the configuration file.

Spec
^^^^

.. note:: | This feature is only fully implemented with the Jenkins automation system.
          | It is partially supported with Zuul (The option will work but will not provide the complete specification)

`cibyl spec JOB_NAME` allows you to easily get the full OpenStack specification of a single job.

The idea behind it is to allow the user to quickly get information on which OpenStack services and features
are covered by a single job so the user doesn't have to go and deep dive into the job configuration and build
artifacts to figure it out by himself.

An example of an output from running `cibyl spec JOB_NAME`::

    Openstack deployment:
      Release: 17.0
      Infra type: virt
      Topology: compute:2,controller:3,ironic:2
      Network:
        IP version: 4
        Network backend: geneve
        ML2 driver: ovn
        Security group mechanism: native ovn
        DVR: True
        TLS everywhere: False
      Storage:
        Cinder backend: lvm
      Ironic:
        Ironic inspector: True
        Cleaning network: False

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
     - |:ballot_box_with_check:|
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:black_square_button:|
   * - --release
     - | OpenStack Release
       | (OSP and RDO supported)
     - |:ballot_box_with_check:|
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
   * - --infra-type
     - | The infrastructure on which
       | OS is deployed (e.g. ovb,
       | baremetal, virthost)
     - |:ballot_box_with_check:|
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
   * - --topology
     - | The combination of node
       | types deployed
     - |:ballot_box_with_check:|
     - |:ballot_box_with_check:|
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:black_square_button:|
   * - --nodes
     - | List of nodes on the topology.
     - |:ballot_box_with_check:|
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
   * - --controllers
     - | Number of controllers
       | (Can be also range: ">=3")
     - |:ballot_box_with_check:|
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
   * - --computes
     - | Number of computes
       | (Can be also range: ">=3")
     - |:ballot_box_with_check:|
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
   * - --ml2-driver
     - | Which ml2 driver does
       | the deployment use
     - |:ballot_box_with_check:|
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
   * - --network-backend
     - | What network protocol is
       | used (e.g. vxlan, vlan, ...)
     - |:ballot_box_with_check:|
     - |:ballot_box_with_check:|
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:black_square_button:|
   * - --cinder-backend
     - | What cinder backend is
       | used (vlan, Ceph, Netapp, nfs)
     - |:ballot_box_with_check:|
     - |:ballot_box_with_check:|
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:black_square_button:|
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
     - |:x:|
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
   * - --test-setup
     - | Source of test setup (rpm, git)
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
