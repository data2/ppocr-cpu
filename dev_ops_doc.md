

# gpu-docker-setup

```bash
# 切换到工作目录下
cd /home/Projects
# 首次运行需创建一个docker容器，再次运行时不需要运行当前命令
# 创建一个名字为ppocr的docker容器，并将当前目录映射到容器的/paddle目录下

#如果您希望在CPU环境下使用docker，使用docker而不是nvidia-docker创建docker
sudo docker run --name ppocr -v $PWD:/paddle --network=host -it registry.baidubce.com/paddlepaddle/paddle:2.1.3-gpu-cuda10.2-cudnn7 /bin/bash

#如果使用CUDA10，请运行以下命令创建容器，设置docker容器共享内存shm-size为64G，建议设置32G以上
# 如果是CUDA11+CUDNN8，推荐使用镜像registry.baidubce.com/paddlepaddle/paddle:2.1.3-gpu-cuda11.2-cudnn8
sudo nvidia-docker run --name ppocr -v $PWD:/paddle --shm-size=64G --network=host -it registry.baidubce.com/paddlepaddle/paddle:2.1.3-gpu-cuda10.2-cudnn7 /bin/bash

# ctrl+P+Q可退出docker 容器，重新进入docker 容器使用如下命令
sudo docker container exec -it ppocr /bin/bash
`



# cpu-docker-setup

```bash

sudo docker run --name ppocr-cpu -v $PWD:/paddle --network=host -it registry.baidubce.com/paddlepaddle/paddle:2.6.1 /bin/bash

`