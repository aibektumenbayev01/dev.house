запуск:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```
неверный URL с 422:

![неверный URL с 422](swagger-ui.png)
