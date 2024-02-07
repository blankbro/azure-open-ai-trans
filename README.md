### Azure OpenAI Translation

基于 Azure OpenAI 开发的翻译工具

### 本地部署

Please ensure you have Python 3.9+ installed.

Create `venv` environment for Python:

```console
python -m venv .venv

# 进入虚拟环境
source .venv/bin/activate

# 退出虚拟环境
deactivate
```

Install `PIP` Requirements

```console
pip install -r requirements.txt
```

configure your .env as Environment variables

```
cp .env.template .env
vi .env # or use whatever you feel comfortable with
```

run

```console
python src/app.py
```