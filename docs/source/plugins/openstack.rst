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
   :widths: 25 25 25 25 25 25
   :header-rows: 1

   * - Argument / Source
     - Jenkins
     - Zuul API
     - Elasticsearch
     - JJB
     - Zuul.d
   * - --ip-version
     - |:ballot_box_with_check:|
     - |:x:|
     - |:x:|
     - |:x:|
     - |:x:|
   * - --release
     - |:ballot_box_with_check:|
     - |:x:|
     - |:x:|
     - |:x:|
     - |:x:|
   * - --topology
     - |:ballot_box_with_check:|
     - |:x:|
     - |:x:|
     - |:x:|
     - |:x:|
   * - --controllers
     - |:x:|
     - |:x:|
     - |:x:|
     - |:x:|
     - |:x:|
   * - --computes
     - |:x:|
     - |:x:|
     - |:x:|
     - |:x:|
     - |:x:|
   * - --dvr
     - |:x:|
     - |:x:|
     - |:x:|
     - |:x:|
     - |:x:|
   * - --network-backend
     - |:x:|
     - |:x:|
     - |:x:|
     - |:x:|
     - |:x:|
   * - --storage-backend
     - |:x:|
     - |:x:|
     - |:x:|
     - |:x:|
     - |:x:|
   * - --packages
     - |:x:|
     - |:x:|
     - |:x:|
     - |:x:|
     - |:x:|
   * - --tls-everywhere
     - |:x:|
     - |:x:|
     - |:x:|
     - |:x:|
     - |:x:|
   * - --containers
     - |:x:|
     - |:x:|
     - |:x:|
     - |:x:|
     - |:x:|
