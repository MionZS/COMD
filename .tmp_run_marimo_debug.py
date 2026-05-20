import runpy, traceback

try:
    runpy.run_path('src/trabalho2/trabalho2_mvp_marimo.py', run_name='not_main')
    print('OK')
except Exception:
    traceback.print_exc()
