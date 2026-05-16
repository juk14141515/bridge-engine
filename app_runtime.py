from app import app
from bridge_core.runtime_api import register_runtime_api

register_runtime_api(app)


@app.get('/api/health')
def runtime_health():
    return {
        'ok': True,
        'service': 'bridge-runtime',
        'version': 'runtime-v2',
        'status': 'ready',
    }


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=6060, debug=True)
