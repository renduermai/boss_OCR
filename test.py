from models import get_tx_model_client, get_ali_model_client

model=get_tx_model_client()
model1=get_ali_model_client()

print(model.invoke("你好你是谁").content)
print(model1.invoke("你好你是谁").content)
