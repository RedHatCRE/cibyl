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
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
   * - --release
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
   * - --infra-type
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
   * - --topology
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
   * - --controllers
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
   * - --computes
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
   * - --dvr
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
   * - --network-backend
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
   * - --storage-backend
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
   * - --packages
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:x:|
     - |:x:|
   * - --tls-everywhere
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:x:|
     - |:x:|
   * - --containers
     - |:black_square_button:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:x:|
     - |:x:|
