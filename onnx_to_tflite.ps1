onnx2tf.exe -i .\ocr\cnn_model.onnx
cp .\saved_model\cnn_model_float16.tflite  ./android/app/src/main/assets/cnn_model.tflite