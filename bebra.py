from yandex_cloud_ml_sdk import YCloudML

sdk = YCloudML(folder_id="b1gmabqgljp5vbjve7re", auth="AQVN3MyWJEvb9W6HxDlirajmBBlXM9q9gbTZFg1r")

model = sdk.models.completions('yandexgpt')
model = model.configure(temperature=0.5)
result = model.run("Что такое небо?")

for alternative in result:
    print(alternative)
