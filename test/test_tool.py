from tools.Pneumonia_tool import predict_pneumonia
result = predict_pneumonia.invoke({'image_path':'test/pneumonia.png'})

print(result)