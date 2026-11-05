import importlib, sys
mods = ['joblib','pandas','sklearn','onnxruntime','skl2onnx']
for m in mods:
    try:
        importlib.import_module(m)
        print(m, 'available')
    except Exception as e:
        print(m, 'MISSING', e)

