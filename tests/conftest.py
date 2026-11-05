# On Windows, onnxruntime must be loaded before certain native runtime libraries
# to prevent DLL initialization conflicts with other C-extensions.
try:
    import onnxruntime
except Exception:
    pass

