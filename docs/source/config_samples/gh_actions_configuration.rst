::

  environments:                     # List of CI/CD environments
    github:                         # An environment called "github"
      github_actions:               # A single system called "github_actions"
        system_type: github_actions # The type of the system (jenkins, zuul or github_actions)
        sources:                    # List of sources belong to "github_actions" system
          jjb:                      # The name of the source which belongs to "production_jenkins" system
            driver: github_actions  # The driver the source will be using
            repos:                  # List of repositories that will be queried when quering the system
                - name: 'rhos-infra/cibyl'
