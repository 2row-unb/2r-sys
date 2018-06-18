# Docker Main Commands

* To build the image:

    ```bash
    sudo docker-compose -f docker/build.yml build
    ```

* To start the system:

    ```bash
    sudo docker-compose -f docker/start.yml run --rm 2r-sys
    ```

* To run bash without starting the system:

    ```bash
    sudo docker-compose -f docker/start.yml run --rm 2r-sys bash
    ```
