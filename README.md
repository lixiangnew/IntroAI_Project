# IntroAI_Project
人工智能导论课程项目作业

## LLM模型api

### 1.获取api
前往<a href = "https://xinghuo.xfyun.cn/sparkapi" target = "_blank">讯飞星火</a>获取apipassword与接口地址(https)
注意该项目使用的模型为 **Spark Max**

### 2.设置环境变量
```bash
set LLM_PROMPT_API_URL your_url
set LLM_PROMPT_API_PASSWORD your_password
```

## 后端

### 1.环境配置
点击<a href = "https://huggingface.co/AmazarashiEndure/Chinese_Landscape_Painting_Generating_Lora_Model_based_on_flux.1">LoRA</a>获取LoRA文件

点击<a href = "https://huggingface.co/black-forest-labs/FLUX.1-dev">Flux 1.0模型</a>下载基础模型全部文件

将<b>model.py</b>中的<b>MODEL_ROOT</b>与<b>LORA_PATH</b>设置为你保存的路径
### 2.使用conda管理依赖
```bash
cd backend
conda env create -f environment.yml
```

### 3.激活环境
```bash
conda activate CN_ShanShui_Model
```

### 4.运行服务器
```bash
cd backend
python app.py
```

## 前端

### 1.下载nvm
前往<a href = "https://github.com/coreybutler/nvm-windows/releases" target = "_blank">nvm-windows</a>下载

### 2.安装Node.js
```bash
nvm install 20
nvm use 20
```

### 3.安装依赖
```bash
cd frontend
npm install
```

### 4.运行服务器
```bash
npm run dev
```

