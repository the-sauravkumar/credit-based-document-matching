import google.generativeai as genai

genai.configure(api_key="AIzaSyCNmInJ-0qqeEK8zGCryBtBK10MNpUR8Hk")

models = genai.list_models()
for model in models:
    print(model.name)
