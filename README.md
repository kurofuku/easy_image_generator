# easy_image_generator



## Overview
This service is wrapper of AUTOMATIC1111/Stable Diffusion.

## Prerequisites
- docker
- docker-compose

## How to use
### Clone https://github.com/AbdBarho/stable-diffusion-webui-docker.git
### Copy service/frondend directory into stable-diffusion-webui-docker cloned directory.
### Change below contents.
```diff
diff --git a/services/AUTOMATIC1111/Dockerfile b/services/AUTOMATIC1111/Dockerfile
index d595784..4d63f7f 100644
--- a/services/AUTOMATIC1111/Dockerfile
+++ b/services/AUTOMATIC1111/Dockerfile
@@ -14,7 +14,7 @@ RUN . /clone.sh generative-models https://github.com/Stability-AI/generative-mod
 RUN . /clone.sh stable-diffusion-webui-assets https://github.com/AUTOMATIC1111/stable-diffusion-webui-assets 6f7db241d2f8ba7457bac5ca9753331f0c266917


-FROM pytorch/pytorch:2.3.0-cuda12.1-cudnn8-runtime
+FROM pytorch/pytorch:2.9.1-cuda13.0-cudnn9-runtime

 ENV DEBIAN_FRONTEND=noninteractive PIP_PREFER_BINARY=1

@@ -30,9 +30,10 @@ WORKDIR /
 RUN --mount=type=cache,target=/root/.cache/pip \
   git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git && \
   cd stable-diffusion-webui && \
-  git reset --hard v1.9.4 && \
+  git reset --hard v1.10.1 && \
   pip install -r requirements_versions.txt

+RUN pip install -U typing_extensions

 ENV ROOT=/stable-diffusion-webui

@@ -40,7 +41,7 @@ COPY --from=download /repositories/ ${ROOT}/repositories/
 RUN mkdir ${ROOT}/interrogate && cp ${ROOT}/repositories/clip-interrogator/clip_interrogator/data/* ${ROOT}/interrogate

 RUN --mount=type=cache,target=/root/.cache/pip \
-  pip install pyngrok xformers==0.0.26.post1 \
+  pip install pyngrok xformers \
   git+https://github.com/TencentARC/GFPGAN.git@8d2447a2d918f8eba5a4a01463fd48e45126a379 \
   git+https://github.com/openai/CLIP.git@d50d76daa670286dd6cacf3bcd80b5e4823fc8e1 \
   git+https://github.com/mlfoundations/open_clip.git@v2.20.0
@@ -55,7 +56,7 @@ COPY . /docker
 RUN \
   # mv ${ROOT}/style.css ${ROOT}/user.css && \
   # one of the ugliest hacks I ever wrote \
-  sed -i 's/in_app_dir = .*/in_app_dir = True/g' /opt/conda/lib/python3.10/site-packages/gradio/routes.py && \
+  sed -i 's/in_app_dir = .*/in_app_dir = True/g' /opt/conda/lib/python3.11/site-packages/gradio/routes.py && \
   git config --global --add safe.directory '*'

 WORKDIR ${ROOT}
diff --git a/services/download/links.txt b/services/download/links.txt
index 3616449..7717960 100644
--- a/services/download/links.txt
+++ b/services/download/links.txt
@@ -14,3 +14,7 @@ https://heibox.uni-heidelberg.de/f/31a76b13ea27482981b4/?dl=1
   out=LDSR/project.yaml
 https://heibox.uni-heidelberg.de/f/578df07c8fc04ffbadf3/?dl=1
   out=LDSR/model.ckpt
+https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
+  out=Stable-diffusion/sd_xl_base_1.0.safetensors
+https://huggingface.co/stabilityai/stable-diffusion-xl-refiner-1.0/resolve/main/sd_xl_refiner_1.0.safetensors
+  out=Stable-diffusion/sd_xl_refiner_1.0.safetensors
```
### Add below entry into docker-compose.yml
```yaml
  frontend:
    profiles: ["frontend"]
    build:
      context: ./services/frontend/
    ports:
      - "8502:8502"
      environment:
        SD_API_HOST: <Your Stable diffusion host and port>
        SD_MODEL_NAME: sd_xl_refiner_1.0.safetensors # This can be your favorite model
        DEFAULT_OLLAMA_HOST: <Your ollama host and port>
        OLLAMA_MODEL_NAME: mixtral # This can be your favorite model
```
### Change docker-compose.yml
```yaml
diff --git a/docker-compose.yml b/docker-compose.yml
index 970b612..42aed45 100644
--- a/docker-compose.yml
+++ b/docker-compose.yml
@@ -29,7 +29,7 @@ services:
     build: ./services/AUTOMATIC1111
     image: sd-auto:78
     environment:
-      - CLI_ARGS=--allow-code --medvram --xformers --enable-insecure-extension-access --api
+      - CLI_ARGS=--allow-code --medvram --opt-sdp-attention --enable-insecure-extension-access --api

   auto-cpu:
     <<: *automatic
```
### Download model for Stable Diffusion
```bash
  (sudo) docker-compose -profile download build
```
### Build container
```bash
  (sudo) docker-compose -profile auto build
  (sudo) docker-compose -profile frontend build
```
### Run container
```bash
  (sudo) docker-compose -profile auto up -d
  (sudo) docker-compose -profile frontend up -d
```
### Access frontend host by your browser

That's it.

